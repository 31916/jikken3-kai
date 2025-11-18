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

// 表・グラフ切り替え（地域）
(function () {
    const graph = document.getElementById("regionGraph");
    const table = document.getElementById("regionTable");
    if (!graph || !table) return;

    document.getElementById("regionGraphBtn").onclick = () => {
        graph.style.display = "block";
        table.style.display = "none";
    };
    document.getElementById("regionTableBtn").onclick = () => {
        graph.style.display = "none";
        table.style.display = "block";
    };
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

// 表・グラフ切り替え（セグメント）
(function () {
    const graph = document.getElementById("segGraph");
    const table = document.getElementById("segTable");
    if (!graph || !table) return;

    document.getElementById("segGraphBtn").onclick = () => {
        graph.style.display = "block";
        table.style.display = "none";
    };
    document.getElementById("segTableBtn").onclick = () => {
        graph.style.display = "none";
        table.style.display = "block";
    };
})();
