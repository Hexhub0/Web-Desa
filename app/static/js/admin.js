document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("adminPopulationChart");

    if (!canvas || typeof Chart === "undefined") {
        return;
    }

    const years = JSON.parse(canvas.dataset.years || "[]");
    const counts = JSON.parse(canvas.dataset.counts || "[]");
    const predictionYear = canvas.dataset.predictionYear;
    const predictionValue = canvas.dataset.predictionValue;

    const hasPrediction =
        predictionYear !== "" &&
        predictionYear !== "null" &&
        predictionValue !== "" &&
        predictionValue !== "null";

    const labels = years.map(String);
    const actualData = [...counts];
    const predictionData = counts.map((value, index) =>
        index === counts.length - 1 ? value : null
    );

    if (hasPrediction && years.length > 0) {
        labels.push(String(predictionYear));
        actualData.push(null);
        predictionData.push(Number(predictionValue));
    }

    if (years.length === 0) {
        return;
    }

    new Chart(canvas, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Data Penduduk",
                    data: actualData,
                    borderColor: "#16794b",
                    backgroundColor: "rgba(22, 121, 75, 0.12)",
                    pointBackgroundColor: "#16794b",
                    borderWidth: 3,
                    pointRadius: 4,
                    tension: 0.25
                },
                {
                    label: "Prediksi",
                    data: predictionData,
                    borderColor: "#e49b26",
                    pointBackgroundColor: "#e49b26",
                    borderWidth: 3,
                    borderDash: [7, 5],
                    pointRadius: 5,
                    tension: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false
            },
            plugins: {
                legend: {
                    position: "bottom"
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            if (context.raw === null) {
                                return null;
                            }

                            return context.dataset.label + ": " +
                                Number(context.raw).toLocaleString("id-ID") +
                                " jiwa";
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: "Tahun"
                    }
                },
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: "Jumlah Penduduk (jiwa)"
                    },
                    ticks: {
                        callback: function (value) {
                            return Number(value).toLocaleString("id-ID");
                        }
                    }
                }
            }
        }
    });
});
