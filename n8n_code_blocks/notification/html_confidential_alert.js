const d = $input.first().json;

const subject = `🚨 [CONFIDENTIAL] Document flagged: ${d.filename}`;

const html = `
<h2 style="color:#DC2626;">🚨 Confidential Document Detected</h2>
<p style="font-family:sans-serif;background:#FFF1F2;padding:12px;border-left:4px solid #DC2626;">
  A document classified as <b>CONFIDENTIAL</b> has been processed and requires immediate review.
</p>
<table style="border-collapse:collapse;width:100%;font-family:sans-serif;font-size:14px;">
  <tr><td style="padding:8px;background:#FFF1F2;"><b>File</b></td><td style="padding:8px;">${d.filename}</td></tr>
  <tr><td style="padding:8px;background:#FFF1F2;"><b>Classification</b></td><td style="padding:8px;">${d.classification}</td></tr>
  <tr><td style="padding:8px;background:#FFF1F2;"><b>Department</b></td><td style="padding:8px;">${d.department}</td></tr>
  <tr><td style="padding:8px;background:#FFF1F2;"><b>Routing Tag</b></td><td style="padding:8px;">${d.routing_tag}</td></tr>
</table>
<p style="font-family:sans-serif;"><b>Summary:</b> ${d.summary}</p>
<hr/>
<p style="font-size:12px;color:#94A3B8;">Document ID: ${d.document_id} · Processed: ${d.processed_at}</p>
`;

return [{ json: { ...d, emailSubject: subject, emailHtml: html } }];
