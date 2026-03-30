require('dotenv').config({ path: '../.env' });
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const cheerio = require('cheerio');
const nodeCron = require('node-cron');
const fs = require('fs');
const path = require('path');
const { Telegraf } = require('telegraf');
const twilio = require('twilio');

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// --- Configuration ---
const RSS_FEEDS = [
    "https://pv-magazine-usa.com/feed/",
    "https://www.solarpowerworldonline.com/feed/",
    "https://cleantechnica.com/feed/",
    "https://electrek.co/feed/",
];

const COMPETITORS = {
    "Wattmonk": "https://www.wattmonk.com",
    "Ensite": "https://www.ensite.com",
    "Tata Power Solar": "https://www.tatapowersolar.com",
    "Loom Solar": "https://www.loomsolar.com",
    "SolarAPP+": "https://solarapp.nrel.gov",
    "Scanifly": "https://scanifly.com",
    "Aurora Solar": "https://aurorasolar.com",
    "Helioscope": "https://helioscope.aurorasolar.com",
    "OpenSolar": "https://www.opensolar.com",
    "SolarPermitPro": "https://www.solarpermitpro.com",
    "Permit Engines": "https://www.permitengines.com",
    "Fast Permit": "https://fastpermit.com",
    "Hover": "https://hover.to",
    "EagleView": "https://www.eagleview.com",
    "Nearmap": "https://www.nearmap.com",
    "SolarNexus": "https://www.solarnexus.com",
    "Energy Toolbase": "https://www.energytoolbase.com",
};

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
// Using 2.0-flash as 2.5 is not a valid version yet
const GEMINI_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${GEMINI_API_KEY}`;
// --- Utils ---
const splitMessage = (text, limit = 4000) => {
    const chunks = [];
    let current = "";
    const lines = text.split('\n');
    for (const line of lines) {
        if ((current.length + line.length + 1) > limit) {
            if (current.trim()) chunks.push(current.trim());
            current = "";
        }
        if (line.length > limit) {
            let tempLine = line;
            while (tempLine.length > limit) {
                chunks.push(tempLine.substring(0, limit));
                tempLine = tempLine.substring(limit);
            }
            current = tempLine + "\n";
        } else {
            current += line + "\n";
        }
    }
    if (current.trim()) chunks.push(current.trim());
    return chunks;
};

// --- Scraper ---
async function fetchNews() {
    console.log("Fetching solar news...");
    let articles = [];
    for (const url of RSS_FEEDS) {
        try {
            const res = await axios.get(url, { timeout: 10000 });
            const $ = cheerio.load(res.data, { xmlMode: true });
            $('item').slice(0, 3).each((i, el) => {
                articles.push({
                    title: $(el).find('title').text(),
                    link: $(el).find('link').text(),
                    summary: $(el).find('description').text().substring(0, 300),
                    source: url
                });
            });
        } catch (e) {
            console.error(`Failed news ${url}: ${e.message}`);
        }
    }
    return articles;
}

async function scrapeCompetitor(name, url) {
    try {
        const res = await axios.get(url, {
            headers: { 'User-Agent': 'Mozilla/5.0' },
            timeout: 10000
        });
        const $ = cheerio.load(res.data);
        const text = $('body').text().replace(/\s+/g, ' ').substring(0, 500);
        return { name, url, snapshot: text };
    } catch (e) {
        return { name, url, snapshot: "Limited external data available." };
    }
}

// --- Agent Logic ---
async function runAgent() {
    console.log("Running AI Solar Industry Analyst...");
    const news = await fetchNews();
    const competitors = await Promise.all(
        Object.entries(COMPETITORS).map(([n, u]) => scrapeCompetitor(n, u))
    );

    const prompt = `TODAY DATA:\n${JSON.stringify(news.slice(0, 5), null, 2)}\n\nCOMPETITORS:\n${JSON.stringify(competitors, null, 2)}\n\nGenerate a HIGHLY CONCISE executive report.`;

    const systemPrompt = `You are a Senior Solar Market Analyst. Your goal is to provide a "30-second read" intelligence report. 

STRICT GUIDELINES FOR CONCISENESS:
1. NO FLUFF: Skip introductory sentences. Go straight to data.
2. BULLET POINTS ONLY: Max 3 points per section.
3. CONCISE RATING: In the Quick-View, use exactly one emoji per line.
4. SO WHAT: Keep the "So What?" to a single sentence only.
5. TABLE: Keep the table narrow and extremely brief.

🏆 EXECUTIVE FORMAT:

### 1. ⚡ Market Pulse (Top 3)
* **[Brief News Headline]**
  - ! Impact: [One sentence business takeaway]

### 2. 📊 Competitor Snap-Shot
* **Wattmonk**: Speed ⭐⭐⭐ | Price ⭐⭐ | Quality ⭐⭐⭐
* **Ensite**: Speed ⭐⭐ | Price ⭐⭐⭐ | Quality ⭐⭐
* **Others**: (Summarize top 2 others briefly)

### 3. 🛡️ Head-to-Head (Wattmonk vs Ensite)
- **Edge**: [Where person A wins]
- **Risk**: [Where person B wins]

### 4. 🚀 Priority Action
- **Do This**: [One specific business action]

### 5. 📢 Dashboard Summary (Short)
(A 3-line summary for mobile users with emojis)`;

    const payload = {
        contents: [{ parts: [{ text: prompt }] }],
        system_instruction: {
            parts: [{ text: systemPrompt }]
        }
    };

    try {
        const res = await axios.post(GEMINI_URL, payload);
        const reportText = res.data.candidates[0].content.parts[0].text;

        const reportDir = path.join(__dirname, 'reports');
        if (!fs.existsSync(reportDir)) fs.mkdirSync(reportDir);
        const fileName = `report_${new Date().toISOString().split('T')[0]}.md`;
        fs.writeFileSync(path.join(reportDir, fileName), reportText);

        await sendNotifications(reportText);
        return { report: reportText, date: new Date() };
    } catch (e) {
        console.error("Agent failed:", e.response?.data || e.message);
        throw e;
    }
}

async function sendNotifications(report) {
    if (process.env.TELEGRAM_TOKEN && process.env.TELEGRAM_CHAT_ID) {
        try {
            const bot = new Telegraf(process.env.TELEGRAM_TOKEN);
            const reportChunks = splitMessage(report);
            for (const chunk of reportChunks) {
                await bot.telegram.sendMessage(process.env.TELEGRAM_CHAT_ID, chunk);
            }
        } catch (e) {
            console.error("Telegram error:", e.message);
        }
    }
}

// --- API Routes ---
app.get('/api/latest-report', (req, res) => {
    const reportDir = path.join(__dirname, 'reports');
    if (!fs.existsSync(reportDir)) return res.json({ error: "No reports found" });
    const files = fs.readdirSync(reportDir).sort().reverse();
    if (files.length === 0) return res.json({ error: "No reports found" });
    const content = fs.readFileSync(path.join(reportDir, files[0]), 'utf-8');
    res.json({ report: content, date: files[0].replace('report_', '').replace('.md', '') });
});

app.post('/api/run-agent', async (req, res) => {
    try {
        const result = await runAgent();
        res.json(result);
    } catch (e) {
        res.status(500).json({ error: e.message });
    }
});

// Run daily 7am IST (1:30 AM UTC)
nodeCron.schedule('30 1 * * *', () => {
    console.log("Running daily 7am IST report...");
    runAgent().catch(console.error);
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
