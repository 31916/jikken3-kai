// -----------------------
// 地域別売上棒グラフ
// -----------------------
const regionData = window.regionDataFromFlask;
(function () {
    const ctx = document.getElementById("regionBarChart");
    if (!ctx || !regionData || regionData.length === 0) return;

    const labels = regionData.map(d => d.area);
    const sales = regionData.map(d => d.total_sales);

    new Chart(ctx.getContext("2d"), {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "地域別売上",
                data: sales,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    ticks: {
                        callback: val => "¥" + Number(val).toLocaleString()
                    }
                }
            }
        }
    });
})();

// -----------------------
// セグメント（年代×性別）積み上げ棒グラフ
// -----------------------
const segData = window.segDataFromFlask;
(function () {
    const ctx = document.getElementById("segStackBar");
    if (!ctx || !segData || segData.length === 0) return;

    const ageGroups = [...new Set(segData.map(d => d.age_group))].sort((a, b) => a - b);

    const maleData = ageGroups.map(a => {
        const row = segData.find(d => d.age_group === a && d.sex === 1);
        return row ? row.total_sales : 0;
    });

    const femaleData = ageGroups.map(a => {
        const row = segData.find(d => d.age_group === a && d.sex === 2);
        return row ? row.total_sales : 0;
    });

    new Chart(ctx.getContext("2d"), {
        type: "bar",
        data: {
            labels: ageGroups.map(a => a + "代"),
            datasets: [
                { label: "男性", data: maleData, stack: "gender" },
                { label: "女性", data: femaleData, stack: "gender" }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { stacked: true },
                y: {
                    stacked: true,
                    ticks: { callback: v => "¥" + Number(v).toLocaleString() }
                }
            }
        }
    });
})();

// -----------------------
// 日本地図の塗り分け
// -----------------------
(function () {
  const data = window.regionDataFromFlask || [];
  const svg = document.getElementById("japanMapSvg");
  if (!svg || !data.length) return;

  // 売上の最小・最大
  const values = data.map(d => d.total_sales);
  const min = Math.min(...values);
  const max = Math.max(...values) || 1;

  // 売上から色を決める（青→赤のグラデーション）
  function getColor(val) {
    const t = (val - min) / (max - min || 1); // 0〜1
    // tが大きいほど赤っぽく、小さいほど青っぽく
    const r = Math.round(255 * t);
    const g = Math.round(100 * (1 - t));
    const b = Math.round(255 * (1 - t));
    return `rgb(${r}, ${g}, ${b})`;
  }

  data.forEach(region => {
    const name = region.area;
    const val = region.total_sales;
    const el = svg.querySelector(`[data-area="${name}"]`);
    if (!el) return;
    el.style.fill = getColor(val);
    el.setAttribute("title", `${name}: ¥${Number(val).toLocaleString()}`);
  });
})();

// -----------------------
// 地域：地図 / グラフ / 表 切り替え
// -----------------------
(function () {
  const mapDiv   = document.getElementById("regionMap");
  const graphDiv = document.getElementById("regionGraph");
  const tableDiv = document.getElementById("regionTable");
  const legend = document.getElementById("colorLegend");

  const mapBtn   = document.getElementById("regionMapBtn");
  const graphBtn = document.getElementById("regionGraphBtn");
  const tableBtn = document.getElementById("regionTableBtn");

  if (!mapDiv || !graphDiv || !tableDiv) return;

  function activate(button) {
    [mapBtn, graphBtn, tableBtn].forEach(b => b && b.classList.remove("active-btn"));
    button && button.classList.add("active-btn");
  }

  mapBtn.onclick = () => {
    mapDiv.style.display   = "block";
    graphDiv.style.display = "none";
    tableDiv.style.display = "none";
    legend.style.display   = "block"; 
    activate(mapBtn);
  };

  graphBtn.onclick = () => {
    mapDiv.style.display   = "none";
    graphDiv.style.display = "block";
    tableDiv.style.display = "none";
    legend.style.display   = "none"; 
    activate(graphBtn);
  };

  tableBtn.onclick = () => {
    mapDiv.style.display   = "none";
    graphDiv.style.display = "none";
    tableDiv.style.display = "block";
    legend.style.display   = "none"; 
    activate(tableBtn);
  };

    if (mapDiv.style.display !== "none") {
    legend.style.display = "block";
  }

})();

(function () {
  const data = window.regionDataFromFlask || [];
  const svg = document.getElementById("japanMapSvg");
  if (!svg || !data.length) return;

  const prefMap = {
  "北海道": "hokkaido",
  "青森県": "aomori",
  "岩手県": "iwate",
  "宮城県": "miyagi",
  "秋田県": "akita",
  "山形県": "yamagata",
  "福島県": "fukushima",
  "茨城県": "ibaraki",
  "栃木県": "tochigi",
  "群馬県": "gunma",
  "埼玉県": "saitama",
  "千葉県": "chiba",
  "東京都": "tokyo",
  "神奈川県": "kanagawa",
  "新潟県": "niigata",
  "富山県": "toyama",
  "石川県": "ishikawa",
  "福井県": "fukui",
  "山梨県": "yamanashi",
  "長野県": "nagano",
  "岐阜県": "gifu",
  "静岡県": "shizuoka",
  "愛知県": "aichi",
  "三重県": "mie",
  "滋賀県": "shiga",
  "京都府": "kyoto",
  "大阪府": "osaka",
  "兵庫県": "hyogo",
  "奈良県": "nara",
  "和歌山県": "wakayama",
  "鳥取県": "tottori",
  "島根県": "shimane",
  "岡山県": "okayama",
  "広島県": "hiroshima",
  "山口県": "yamaguchi",
  "徳島県": "tokushima",
  "香川県": "kagawa",
  "愛媛県": "ehime",
  "高知県": "kochi",
  "福岡県": "fukuoka",
  "佐賀県": "saga",
  "長崎県": "nagasaki",
  "熊本県": "kumamoto",
  "大分県": "oita",
  "宮崎県": "miyazaki",
  "鹿児島県": "kagoshima",
  "沖縄県": "okinawa"
};


  // 売上の min / max
  const values = data.map(d => d.total_sales);
  const min = Math.min(...values);
  const max = Math.max(...values) || 1;

  // 色決定（青 → 赤）
  function getColor(val) {
    const t = (val - min) / (max - min || 1);
    const r = Math.round(255 * t);
    const g = Math.round(100 * (1 - t));
    const b = Math.round(255 * (1 - t));
    return `rgb(${r}, ${g}, ${b})`;
  }

  // 各県を塗る
  data.forEach(region => {
    const jpName = region.area;       // "滋賀県" など
    const key = prefMap[jpName];      // "shiga"
    if (!key) return;

    const el = svg.querySelector(`g.${key}.prefecture`);
    if (!el) return;

    el.style.fill = getColor(region.total_sales);
    el.style.stroke = "#333";
    el.style.strokeWidth = "1";

    // ツールチップ
    el.setAttribute("title", `${jpName}: ¥${Number(region.total_sales).toLocaleString()}`);
  });
})();


// -----------------------
// セグメント（年代×性別） グラフ / 表 切り替え
// -----------------------
(function () {
  const segGraph    = document.getElementById("segGraph");
  const segTable    = document.getElementById("segTable");
  const segGraphBtn = document.getElementById("segGraphBtn");
  const segTableBtn = document.getElementById("segTableBtn");

  if (!segGraph || !segTable || !segGraphBtn || !segTableBtn) return;

  function activateSeg(button) {
    [segGraphBtn, segTableBtn].forEach(b => b && b.classList.remove("active-btn"));
    button && button.classList.add("active-btn");
  }

  segGraphBtn.onclick = () => {
    segGraph.style.display = "block";
    segTable.style.display = "none";
    activateSeg(segGraphBtn);
  };

  segTableBtn.onclick = () => {
    segGraph.style.display = "none";
    segTable.style.display = "block";
    activateSeg(segTableBtn);
  };
})();
