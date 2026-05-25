const text = $input.first().json.parsed?.full_text ?? $input.first().json.full_text ?? "";

// Prefer AI-detected scenario, fall back to env var, then default
const scenario = $input.first().json.detected_scenario ?? "business";

const personas = {
  business: {
    role: "You are an expert business document intelligence assistant with deep knowledge of corporate communications, contracts, and operational documents.",
    focus: "Focus on business impact, stakeholder actions, financial figures, and organizational entities.",
  },
  cybersecurity: {
    role: "You are an expert cybersecurity analyst specializing in incident reports, threat intelligence, and security audit documents.",
    focus: "Focus on threat actors, CVEs, affected systems, severity levels, and remediation steps.",
  },
  financial: {
    role: "You are an expert financial analyst with deep knowledge of financial statements, investment reports, and market documents.",
    focus: "Focus on monetary amounts, financial ratios, time periods, risk indicators, and recommended actions.",
  },
  hr: {
    role: "You are an expert HR document specialist with deep knowledge of employment contracts, performance reviews, and HR policies.",
    focus: "Focus on employee names, roles, dates, policy changes, and action items for HR teams.",
  },
  product: {
    role: "You are an expert product analyst specializing in product descriptions, specifications, and market positioning documents.",
    focus: "Focus on product features, target audience, competitive differentiators, and pricing information.",
  },
  academic: {
    role: "You are an expert academic research analyst with broad knowledge across scientific disciplines.",
    focus: "Focus on research objectives, methodologies, key findings, citations, and future research directions.",
  },
  legal: {
    role: "You are an expert legal document analyst with deep knowledge of contracts, regulations, and legal proceedings.",
    focus: "Be precise with party names, dates, obligations, clauses, and deadlines. Flag any ambiguous or high-risk language.",
  },
  medical: {
    role: "You are an expert medical document analyst with deep knowledge of clinical documentation, diagnoses, and treatment plans.",
    focus: "Focus on patient-relevant clinical entities, diagnoses, medications, dosages, and follow-up action items.",
  },
  other: {
    role: "You are a general-purpose document intelligence assistant capable of analyzing any type of document.",
    focus: "Focus on the main subject, key entities, dates, monetary amounts, and any clear action items or decisions.",
  },
};

const persona = personas[scenario] ?? personas.business;

const prompt = `## Role
${persona.role}

## Task
Analyze the document text provided below and extract structured intelligence from it.
${persona.focus}

## Example

<example>
  <input>
    Acme Corp signed a service agreement with TechVendor Ltd on March 12, 2024 for $48,000 annually.
    John Smith (CTO) must approve the renewal by April 1, 2024. The terms include a 30-day termination clause.
  </input>
  <output>
    {
      "summary": "Acme Corp entered a $48,000 annual service agreement with TechVendor Ltd on March 12, 2024. The CTO must approve renewal before April 1, 2024. A 30-day termination clause is included.",
      "classification": "contract",
      "sentiment": "neutral",
      "entities": {
        "people":        ["John Smith"],
        "organizations": ["Acme Corp", "TechVendor Ltd"],
        "dates":         ["March 12, 2024", "April 1, 2024"],
        "amounts":       ["$48,000 annually"]
      },
      "action_items": ["John Smith (CTO) must approve renewal by April 1, 2024"],
      "confidence_score": 0.97
    }
  </output>
</example>

## Rules
- If a field has no relevant data, return an empty array \`[]\` or empty string \`""\`.
- Do not invent information. Only extract what is explicitly stated in the document.
- \`confidence_score\` must reflect actual certainty — use the full 0.0–1.0 range.

## Document
${text}`;

const requestBody = {
  contents: [{ parts: [{ text: prompt }] }],
  generationConfig: {
    temperature: 0.2,
    responseMimeType: "application/json",
    responseSchema: {
      type: "object",
      properties: {
        summary: {
          type: "string",
          description: "2-3 sentence factual summary of the document",
        },
        classification: {
          type: "string",
          enum: ["invoice", "report", "contract", "ticket", "article", "other"],
        },
        sentiment: {
          type: "string",
          enum: ["positive", "neutral", "negative"],
        },
        entities: {
          type: "object",
          properties: {
            people:        { type: "array", items: { type: "string" } },
            organizations: { type: "array", items: { type: "string" } },
            dates:         { type: "array", items: { type: "string" } },
            amounts:       { type: "array", items: { type: "string" } },
          },
        },
        action_items: {
          type: "array",
          items: { type: "string" },
        },
        confidence_score: {
          type: "number",
        },
      },
      required: ["summary", "classification", "sentiment", "entities", "action_items", "confidence_score"],
    },
  },
};

return [{ json: { ...($input.first().json), requestBody } }];
