const report = $('Generate Report').first().json;
const flash = $('Merge Results - Enrich + Sensitivity').first().json;
const pro = $('Merge Results - Enrich + Sensitivity').last().json;
const flashModel = $('Set Gemini Api Key').first().json.gemini_flash_model;
const proModel = $('Set Gemini Api Key').first().json.gemini_pro_model;

const actionItems = Array.isArray(report.action_items)
  ? report.action_items.map(i => `<li>${i}</li>`).join('')
  : `<li>${report.action_items}</li>`;

const subject = `Prismatic - [${pro.classification}] New document processed: ${report.filename}`;

const html = `
<h2 style="color:#1D4ED8;">📄 Prismatic Document Processed</h2>
<table style="border-collapse:collapse;width:100%;font-family:sans-serif;font-size:14px;">
  <tr><td style="padding:8px;background:#F1F5F9;"><b>File</b></td><td style="padding:8px;">${report.filename}</td></tr>
  ${report.source_zip ? `<tr><td style="padding:8px;background:#F1F5F9;"><b>Source ZIP</b></td><td style="padding:8px;">${JSON.parse(report.source_zip).name}</td></tr>` : ''}
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Department</b></td><td style="padding:8px;">${report.department}</td></tr>
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Sensitivity</b></td><td style="padding:8px;">${report.sensitivity}</td></tr>
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Routing Tag</b></td><td style="padding:8px;">${report.routing_tag}</td></tr>
</table>

<h3 style="margin-top:20px;">Model Comparison</h3>
<table style="border-collapse:collapse;width:100%;font-family:sans-serif;font-size:14px;">
  <tr>
    <th style="padding:8px;background:#1D4ED8;color:white;text-align:left;width:25%;"></th>
    <th style="padding:8px;background:#1D4ED8;color:white;text-align:left;">${flashModel}</th>
    <th style="padding:8px;background:#1D4ED8;color:white;text-align:left;">${proModel}</th>
  </tr>
  <tr>
    <td style="padding:8px;background:#F1F5F9;"><b>Classification</b></td>
    <td style="padding:8px;">${flash.classification}</td>
    <td style="padding:8px;">${pro.classification}</td>
  </tr>
  <tr>
    <td style="padding:8px;background:#F1F5F9;"><b>Sentiment</b></td>
    <td style="padding:8px;">${flash.sentiment}</td>
    <td style="padding:8px;">${pro.sentiment}</td>
  </tr>
  <tr>
    <td style="padding:8px;background:#F1F5F9;"><b>Confidence</b></td>
    <td style="padding:8px;">${flash.confidence_score}</td>
    <td style="padding:8px;">${pro.confidence_score}</td>
  </tr>
</table>

<h3 style="margin-top:20px;">Summary</h3>
<p style="font-family:sans-serif;">${pro.summary}</p>
<h3>Action Items</h3>
<ul style="font-family:sans-serif;">${actionItems}</ul>
<hr/>
<p style="font-size:12px;color:#94A3B8;">Sent automatically by Prismatic · Document ID: ${report.document_id}</p>
`;

return [{ json: { ...report, emailSubject: subject, emailHtml: html } }];
