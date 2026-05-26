const report = $('Generate Report').first().json;

const actionItems = Array.isArray(report.action_items)
  ? report.action_items.map(i => `<li>${i}</li>`).join('')
  : `<li>${report.action_items}</li>`;

const subject = `[${report.classification}] New document processed: ${report.filename}`;

const html = `
<h2 style="color:#1D4ED8;">📄 Document Processed</h2>
<table style="border-collapse:collapse;width:100%;font-family:sans-serif;font-size:14px;">
  <tr><td style="padding:8px;background:#F1F5F9;"><b>File</b></td><td style="padding:8px;">${report.filename}</td></tr>
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Classification</b></td><td style="padding:8px;">${report.classification}</td></tr>
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Department</b></td><td style="padding:8px;">${report.department}</td></tr>
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Sentiment</b></td><td style="padding:8px;">${report.sentiment}</td></tr>
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Sensitivity</b></td><td style="padding:8px;">${report.sensitivity}</td></tr>
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Routing Tag</b></td><td style="padding:8px;">${report.routing_tag}</td></tr>
  <tr><td style="padding:8px;background:#F1F5F9;"><b>Confidence</b></td><td style="padding:8px;">${report.confidence_adjusted}</td></tr>
</table>
<h3 style="margin-top:20px;">Summary</h3>
<p style="font-family:sans-serif;">${report.summary}</p>
<h3>Action Items</h3>
<ul style="font-family:sans-serif;">${actionItems}</ul>
<hr/>
<p style="font-size:12px;color:#94A3B8;">Sent automatically by Prismatic · Document ID: ${report.document_id}</p>
`;

return [{ json: { ...report, emailSubject: subject, emailHtml: html } }];
