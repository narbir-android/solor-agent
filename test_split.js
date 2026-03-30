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

// Test 1: Normal short message
console.log("Test 1: ", splitMessage("Hello World").length === 1);

// Test 2: Message just under limit
const longMsg = "a".repeat(3999);
console.log("Test 2: ", splitMessage(longMsg).length === 1);

// Test 3: Message over limit
const overLimitMsg = "a".repeat(3000) + "\n" + "b".repeat(2000);
console.log("Test 3: ", splitMessage(overLimitMsg).length === 2);

// Test 4: Single line over limit
const superLongLine = "c".repeat(9000);
const chunks4 = splitMessage(superLongLine);
console.log("Test 4: ", chunks4.length === 3, chunks4.map(c => c.length));

// Test 5: Multiple lines
const linesMsg = "line1\nline2\nline3";
console.log("Test 5: ", splitMessage(linesMsg, 10).length === 2); // "line1\nline2" (11 chars) -> "line1" and "line2\nline3"
