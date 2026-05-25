const allItems = $input.all();

const flash = allItems.find(i => i.json.gemini_flash)?.json.gemini_flash ?? {};
const pro   = allItems.find(i => i.json.gemini_pro)?.json.gemini_pro   ?? {};

const diff = {
  classification_match: flash.classification === pro.classification,
  sentiment_match:      flash.sentiment === pro.sentiment,
  flash_confidence:     flash.confidence_score,
  pro_confidence:       pro.confidence_score ?? null,
  flash_summary:        flash.summary,
  pro_summary:          pro.summary ?? null,
};

const scenario = $('Extract Scenario').first().json;
const file     = $('Download file').first().json;

return [{
  json: {
    drive_file_id:      file.id,
    filename:           file.name,
    file_extension:     file.fileExtension,
    mime_type:          file.mimeType,
    detected_scenario:  scenario.detected_scenario,
    scenario_reasoning: scenario.scenario_reasoning,
    gemini_flash:       flash,
    gemini_pro:         pro,
    flash_vs_pro_diff:  diff,
  }
}];
