const raw = $input.first().json;
const text = raw.candidates?.[0]?.content?.parts?.[0]?.text ?? "{}";
const { scenario, reasoning } = JSON.parse(text);

// HTTP Request replaced the data — restore original document fields from before the HTTP call
const original = $('Detect Scenario').first().json;

return [{ json: { ...original, detected_scenario: scenario, scenario_reasoning: reasoning } }];
