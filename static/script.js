function nextStep(stepNumber) {
    const currentStep = document.querySelector('.step.active')
    if (currentStep) {
        currentStep.classList.remove('active')
    }
    const next = document.getElementById('step-' + stepNumber)
    next.classList.add('active')
}

function switchView(view, btn) {
    document.querySelectorAll('.toggle-btn').forEach(function(b) {
        b.classList.remove('active-toggle')
    })
    btn.classList.add('active-toggle')
    if (window.myChartInstance) {
        window.myChartInstance.destroy()
        window.myChartInstance = null
    }
    loadChart(view)
}

function loadChart(view = '30days') {
    fetch('/api/entries')
        .then(function(response) {
            return response.json()
        })
        .then(function(allEntries) {
            let entries = allEntries

            if (view === '30days') {
                const thirtyDaysAgo = new Date()
                thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
                entries = allEntries.filter(function(entry) {
                    const entryDate = new Date(entry.date)
                    return entryDate >= thirtyDaysAgo
                })
            }

            const labels = entries.map(function(entry) {
                const date = new Date(entry.date)
                return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
            })

            const scores = entries.map(function(entry) {
                return entry.score
            })

            const ctx = document.getElementById('myChart').getContext('2d')

            if (window.myChartInstance) {
                window.myChartInstance.destroy()
                window.myChartInstance = null
            }

            window.myChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Loving life',
                        data: scores,
                        borderColor: '#C4714F',
                        backgroundColor: 'rgba(196, 113, 79, 0.1)',
                        borderWidth: 2,
                        pointBackgroundColor: '#C4714F',
                        pointRadius: 3,
                        pointHoverRadius: 5,
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: {
                        duration: 2000,
                        easing: 'easeInOutQuart'
                    },
                    scales: {
                        y: {
                            min: 0,
                            max: 10,
                            grid: {
                                color: 'rgba(154, 140, 130, 0.2)'
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                maxTicksLimit: 10
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            enabled: false,
                            external: function(context) {
                                let tooltipEl = document.getElementById('custom-tooltip')
                                if (!tooltipEl) {
                                    tooltipEl = document.createElement('div')
                                    tooltipEl.id = 'custom-tooltip'
                                    document.body.appendChild(tooltipEl)
                                }

                                const tooltipModel = context.tooltip
                                if (tooltipModel.opacity === 0) {
                                    tooltipEl.style.opacity = '0'
                                    return
                                }

                                const index = tooltipModel.dataPoints[0].dataIndex
                                const entry = entries[index]

                                tooltipEl.innerHTML = `
                                    <p class="tt-date">${tooltipModel.title[0]}</p>
                                    <p class="tt-score">Loving life: ${entry.score}</p>
                                    <p class="tt-label">Grateful for:</p>
                                    <p class="tt-item">• ${entry.grateful[0]}</p>
                                    <p class="tt-item">• ${entry.grateful[1]}</p>
                                    <p class="tt-item">• ${entry.grateful[2]}</p>
                                    <p class="tt-label">Praying for:</p>
                                    <p class="tt-item">• ${entry.prayers[0]}</p>
                                    <p class="tt-item">• ${entry.prayers[1]}</p>
                                    <p class="tt-item">• ${entry.prayers[2]}</p>
                                `

                                const position = context.chart.canvas.getBoundingClientRect()
                                tooltipEl.style.opacity = '1'
                                tooltipEl.style.left = position.left + window.scrollX + tooltipModel.caretX + 'px'
                                tooltipEl.style.top = position.top + window.scrollY + tooltipModel.caretY - tooltipEl.offsetHeight + 10 + 'px'
                            }
                        }
                    }
                }
            })

            const container = document.getElementById('chart-container')
            container.classList.add('loaded')
            container.style.opacity = '1'
        })
}

function toggleHistory() {
    const table = document.getElementById('history-table')
    const btn = document.querySelector('.step-6-btn')
    if (table.style.display === 'none') {
        table.style.display = 'block'
        fetch('/api/entries')
            .then(function(response) {
                return response.json()
            })
            .then(function(entries) {
                const reversed = entries.slice().reverse()
                let html = ''
                reversed.forEach(function(entry) {
                    const date = new Date(entry.date)
                    const formatted = date.toLocaleDateString('en-GB', {
                        weekday: 'long',
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric'
                    })
                    html += '<div class="history-card">'
                    html += '<p class="history-date">' + formatted + '</p>'
                    html += '<p class="history-text">Today I\'m grateful for <em>' + entry.grateful[0] + '</em>, <em>' + entry.grateful[1] + '</em> and <em>' + entry.grateful[2] + '</em>, and I\'m praying about <em>' + entry.prayers[0] + '</em>, <em>' + entry.prayers[1] + '</em> and <em>' + entry.prayers[2] + '</em>.</p>'
                    html += '<p class="history-score">Score: ' + entry.score + '/10</p>'
                    html += '</div>'
                })
                table.innerHTML = html
            })
        btn.textContent = 'Hide entries ↑'
    } else {
        table.style.display = 'none'
        btn.textContent = 'See all past entries ↓'
    }
}

// Single DOMContentLoaded listener — fixes duplicate event handler bug
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('main-form')
    const urlParams = new URLSearchParams(window.location.search)
    const viewJourney = urlParams.get('view') === 'journey'

    if (form) {
        if (viewJourney) {
            nextStep(6)
            loadChart()
        } else {
            const hasName = form.querySelector('input[name="name"][type="hidden"]')
            if (hasName) {
                nextStep(2)
            } else {
                nextStep(1)
            }
        }

        form.addEventListener('submit', function(e) {
            e.preventDefault()
            nextStep(5)
            // Hide chart container so it can fade in after submission
            const chartContainer = document.getElementById('chart-container')
            if (chartContainer) chartContainer.style.opacity = '0'
            setTimeout(function() {
                const formData = new FormData(form)
                fetch('/add', {
                    method: 'POST',
                    body: formData
                })
                .then(function() {
                    nextStep(6)
                    loadChart()
                })
            }, 2500)
        })
    } else {
        loadChart()
    }
})
