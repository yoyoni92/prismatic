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
const file     = $('Start').first().json;

return [{
  json: {
    drive_file_id:      file.id ?? file._sourceZip?.id ?? null,
    filename:           file.name ?? file._fileName,
    file_extension:     file.fileExtension,
    mime_type:          file.mimeType,
    source_zip:         file._sourceZip ? JSON.stringify(file._sourceZip) : null,
    detected_scenario:  scenario.detected_scenario,
    scenario_reasoning: scenario.scenario_reasoning,
    gemini_flash:       flash,
    gemini_pro:         pro,
    flash_vs_pro_diff:  diff,
  }
}];
