const rows = $input.all();

if (rows.length === 0) {
  return [{ json: { skip: true } }];
}

const docs = rows.map(r => r.json);
const count = docs.length;

// unique files + run count per file
const fileRuns = {};
for (const r of docs) {
  fileRuns[r.document_id] = fileRuns[r.document_id] || { ...r, runs: 0 };
  fileRuns[r.document_id].runs++;
}
const uniqueDocs = Object.values(fileRuns);
const uniqueCount = uniqueDocs.length;
const suspiciousCount = uniqueDocs.filter(r => r.runs > 2).length;

// classification breakdown (on unique files)
const byClassification = {};
for (const r of uniqueDocs) {
  const c = r.classification || 'other';
  byClassification[c] = (byClassification[c] || 0) + 1;
}

const subject = `📊 Daily Digest — ${count} runs · ${uniqueCount} files${suspiciousCount > 0 ? ` · ⚠️ ${suspiciousCount} suspicious` : ''}`;

const today = new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

const classificationRows = Object.entries(byClassification).map(([k, v]) => {
  const pct = Math.round((v / uniqueCount) * 100);
  return `
  <tr>
    <td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;font-family:sans-serif;font-size:14px;text-transform:capitalize;">${k}</td>
    <td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;font-family:sans-serif;font-size:14px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <div style="background:#DBEAFE;border-radius:4px;height:8px;width:${pct}px;min-width:4px;"></div>
        <span><b>${v}</b> <span style="color:#94A3B8;">(${pct}%)</span></span>
      </div>
    </td>
  </tr>`;
}).join('');

const sensitivityBadge = s => {
  const colors = { confidential: '#FEE2E2;color:#DC2626', internal: '#FEF9C3;color:#CA8A04', public: '#DCFCE7;color:#16A34A' };
  const style = colors[s] || '#F1F5F9;color:#64748B';
  return `<span style="background:${style};padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600;text-transform:uppercase;">${s}</span>`;
};

const docRows = uniqueDocs.map(r => {
  const suspicious = r.runs > 2;
  const rowBg = suspicious ? '#FFF7ED' : 'white';
  const runsCell = suspicious
    ? `<td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;font-family:sans-serif;font-size:13px;color:#EA580C;font-weight:700;">⚠️ ${r.runs}</td>`
    : `<td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;font-family:sans-serif;font-size:13px;color:#94A3B8;">${r.runs}</td>`;
  return `
  <tr style="background:${rowBg};">
    <td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;font-family:sans-serif;font-size:13px;font-weight:600;">${r.filename}</td>
    <td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;font-family:sans-serif;font-size:13px;text-transform:capitalize;">${r.classification}</td>
    <td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;">${sensitivityBadge(r.sensitivity)}</td>
    <td style="padding:10px 16px;border-bottom:1px solid #E2E8F0;font-family:sans-serif;font-size:13px;color:#64748B;">${r.routing_tag}</td>
    ${runsCell}
  </tr>`;
}).join('');

const html = `
<div style="background:#F8FAFC;padding:32px 0;font-family:sans-serif;">
<div style="max-width:640px;margin:0 auto;background:white;border-radius:12px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

  <!-- Header -->
  <div style="background:linear-gradient(135deg,#1D4ED8 0%,#4F46E5 100%);padding:32px 40px;">
    <div style="font-size:12px;color:#BFDBFE;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">Prismatic · Daily Report</div>
    <div style="font-size:26px;font-weight:700;color:white;">📊 Document Digest</div>
    <div style="font-size:13px;color:#BFDBFE;margin-top:6px;">${today}</div>
  </div>

  <!-- KPI Cards -->
  <div style="display:flex;gap:0;border-bottom:1px solid #E2E8F0;">
    <div style="flex:1;padding:20px 24px;border-right:1px solid #E2E8F0;text-align:center;">
      <div style="font-size:32px;font-weight:700;color:#1D4ED8;">${count}</div>
      <div style="font-size:12px;color:#94A3B8;margin-top:4px;text-transform:uppercase;letter-spacing:1px;">Total Runs</div>
    </div>
    <div style="flex:1;padding:20px 24px;border-right:1px solid #E2E8F0;text-align:center;">
      <div style="font-size:32px;font-weight:700;color:#0F766E;">${uniqueCount}</div>
      <div style="font-size:12px;color:#94A3B8;margin-top:4px;text-transform:uppercase;letter-spacing:1px;">Unique Files</div>
    </div>
    <div style="flex:1;padding:20px 24px;text-align:center;">
      <div style="font-size:32px;font-weight:700;color:${suspiciousCount > 0 ? '#DC2626' : '#94A3B8'};">${suspiciousCount}</div>
      <div style="font-size:12px;color:#94A3B8;margin-top:4px;text-transform:uppercase;letter-spacing:1px;">Suspicious</div>
    </div>
  </div>

  <div style="padding:32px 40px;">

    <!-- Note -->
    <p style="font-size:13px;color:#64748B;margin:0 0 24px 0;">Each file is analyzed by <b>2 models</b> (Flash + Pro). Expected runs = unique files × 2. Runs &gt; 2 per file are flagged as suspicious.</p>

    <!-- Classification -->
    <div style="font-size:13px;font-weight:700;color:#1E293B;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">By Classification</div>
    <table style="width:100%;border-collapse:collapse;border:1px solid #E2E8F0;border-radius:8px;overflow:hidden;margin-bottom:32px;">
      <thead>
        <tr style="background:#F8FAFC;">
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Classification</th>
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Count</th>
        </tr>
      </thead>
      <tbody>${classificationRows}</tbody>
    </table>

    <!-- Documents -->
    <div style="font-size:13px;font-weight:700;color:#1E293B;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">Documents</div>
    <table style="width:100%;border-collapse:collapse;border:1px solid #E2E8F0;border-radius:8px;overflow:hidden;">
      <thead>
        <tr style="background:#F8FAFC;">
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:1px;">File</th>
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Classification</th>
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Sensitivity</th>
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Routing</th>
          <th style="padding:10px 16px;text-align:left;font-size:12px;color:#94A3B8;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Runs</th>
        </tr>
      </thead>
      <tbody>${docRows}</tbody>
    </table>

  </div>

  <!-- Footer -->
  <div style="background:#F8FAFC;padding:20px 40px;border-top:1px solid #E2E8F0;text-align:center;">
    <p style="font-size:12px;color:#94A3B8;margin:0;">Sent automatically by <b>Prismatic</b> · Powered by n8n + Gemini · Daily at 08:00</p>
  </div>

</div>
</div>
`;

return [{ json: { count, uniqueCount, suspiciousCount, rows: docs, byClassification, skip: false, emailSubject: subject, emailHtml: html } }];
