const report = $('Generate Report').first().json;

const subject = `🚨 [CONFIDENTIAL] Document flagged: ${report.filename}`;

const html = `
<h2 style="color:#DC2626;">🚨 Confidential Document Detected</h2>
<p style="font-family:sans-serif;background:#FFF1F2;padding:12px;border-left:4px solid #DC2626;">
  A document classified as <b>CONFIDENTIAL</b> has been processed and requires immediate review.
</p>
<table style="border-collapse:collapse;width:100%;font-family:sans-serif;font-size:14px;">
  <tr><td style="padding:8px;background:#FFF1F2;"><b>File</b></td><td style="padding:8px;">${report.filename}</td></tr>
  <tr><td style="padding:8px;background:#FFF1F2;"><b>Classification</b></td><td style="padding:8px;">${report.classification}</td></tr>
  <tr><td style="padding:8px;background:#FFF1F2;"><b>Department</b></td><td style="padding:8px;">${report.department}</td></tr>
  <tr><td style="padding:8px;background:#FFF1F2;"><b>Routing Tag</b></td><td style="padding:8px;">${report.routing_tag}</td></tr>
</table>
<p style="font-family:sans-serif;"><b>Summary:</b> ${report.summary}</p>
<hr/>
<p style="font-size:12px;color:#94A3B8;">Document ID: ${report.document_id} · Processed: ${report.processed_at}</p>
`;

return [{ json: { ...report, emailSubject: subject, emailHtml: html } }];
