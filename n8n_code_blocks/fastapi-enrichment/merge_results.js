const general_data    = $('Final Result With Models Diff').first().json


return [{
  json: {
    drive_file_id:                general_data.drive_file_id,
    filename:                     general_data.filename,
    file_extension:               general_data.file_extension,
    mime_type:                    general_data.mime_type,

    detected_scenario:            general_data.detected_scenario,
    scenario_reasoning:           general_data.scenario_reasoning,

    ...general_data.gemini_flash,
    gemini_pro:                   general_data.gemini_pro,
    flash_vs_pro_diff:            general_data.flash_vs_pro_diff,

    document_id:                  $input.first().json.document_id,
    department:                   $input.first().json.department,
    routing_tag:                  $input.first().json.routing_tag,
    confidence_adjusted:          $input.first().json.confidence_adjusted,
    keyword_tags:                 $input.first().json.keyword_tags,
    processed_at:                 $('Set Gemini Api Key').first().json.processed_at,

    sensitivity:                  $input.last().json.sensitivity,
    sensitivity_reason:           $input.last().json.reason,
    verified_llm_on_sensitivity:  $input.last().json.llm_verified
  }
}];
