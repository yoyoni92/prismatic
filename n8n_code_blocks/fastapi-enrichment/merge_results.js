const general_data = $('Final Result With Models Diff').first().json;
const enrich       = $input.first().json;
const sens         = $input.last().json;

const flash = general_data.gemini_flash;
const pro   = general_data.gemini_pro;

const shared = {
  document_id:       enrich.document_id,
  drive_file_id:     general_data.drive_file_id,
  filename:          general_data.filename,
  file_type:         general_data.file_extension,
  processed_at:      enrich.processed_at,
  department:        enrich.department,
  sensitivity:       sens.sensitivity,
  routing_tag:       enrich.routing_tag,
  source_zip:        general_data.source_zip ?? null,
  flash_vs_pro_diff: JSON.stringify(general_data.flash_vs_pro_diff),
};

return [
  {
    json: {
      ...shared,
      model:            $('Set Gemini Api Key').first().json.gemini_flash_model,
      classification:   flash.classification,
      sentiment:        flash.sentiment,
      confidence_score: flash.confidence_score,
      summary:          flash.summary.slice(0, 500),
      action_items:     flash.action_items.join(', '),
    }
  },
  {
    json: {
      ...shared,
      model:            $('Set Gemini Api Key').first().json.gemini_pro_model,
      classification:   pro.classification,
      sentiment:        pro.sentiment,
      confidence_score: pro.confidence_score,
      summary:          pro.summary.slice(0, 500),
      action_items:     (pro.action_items ?? []).join(', '),
    }
  }
];
