const items = $input.all();
const total = items.length;
return items.map((item, idx) => ({
  json: { ...item.json, _total: total, _idx: idx }
}));
