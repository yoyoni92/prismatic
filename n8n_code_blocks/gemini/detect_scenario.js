const text = $input.first().json.parsed?.full_text ?? $input.first().json.full_text ?? $input.first().json.pageContent ?? "";
const excerpt = text.slice(0, 1000);

const prompt = `## Task
Read the document excerpt below and classify it into exactly one of these domain scenarios:

- **business**      — general corporate communications, operations, memos
- **cybersecurity** — incident reports, threat intelligence, security audits
- **financial**     — financial statements, investment reports, budgets
- **hr**            — employment contracts, performance reviews, HR policies
- **product**       — product descriptions, specs, market positioning
- **academic**      — research papers, studies, academic articles
- **legal**         — contracts, regulations, legal proceedings, compliance
- **medical**       — clinical notes, diagnoses, treatment plans, lab results
- **other**         — does not clearly fit any of the above domains

## Example

<example>
  <input>This agreement is entered into by and between Acme Corp and John Smith effective January 1, 2024...</input>
  <output>legal</output>
</example>

## Document Excerpt
${excerpt}`;

const requestBody = {
  contents: [{ parts: [{ text: prompt }] }],
  generationConfig: {
    temperature: 0,
    responseMimeType: "application/json",
    responseSchema: {
      type: "object",
      properties: {
        scenario: {
          type: "string",
          enum: ["business", "cybersecurity", "financial", "hr", "product", "academic", "legal", "medical", "other"],
        },
        reasoning: { type: "string" },
      },
      required: ["scenario", "reasoning"],
    },
  },
};

return [{ json: { ...($input.first().json), requestBody } }];
