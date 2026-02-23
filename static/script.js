function nextStep(stepNumber) {
    const currentStep = document.querySelector('.step.active')
    if (currentStep) {
        currentStep.classList.remove('active')
    }
    const next = document.getElementById('step-' + stepNumber)
    next.classList.add('active')
}

function loadChart() {
    fetch('/api/entries')
        .then(function(response) {
            return response.json()
        })
        .then(function(entries) {
            const labels = entries.map(function(entry) {
    const date = new Date(entry.date)
    return date.getDate()
})

            const scores = entries.map(function(entry) {
                return entry.score
            })

            const ctx = document.getElementById('myChart').getContext('2d')

            new Chart(ctx, {
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
                        pointRadius: 6,
                        pointHoverRadius: 8,
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
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
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                afterBody: function(context) {
                                    const entry = entries[context[0].dataIndex]
                                    return [
                                        '',
                                        'Grateful for:',
                                        '• ' + entry.grateful[0],
                                        '• ' + entry.grateful[1],
                                        '• ' + entry.grateful[2],
                                        '',
                                        'Praying for:',
                                        '• ' + entry.prayers[0],
                                        '• ' + entry.prayers[1],
                                        '• ' + entry.prayers[2]
                                    ]
                                }
                            }
                        }
                    }
                }
            })
        })
}

function toggleHistory() {
    const table = document.getElementById('history-table')
    const btn = document.querySelector('#step-6 button')
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

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('main-form')
    if (form) {
        nextStep(1)
        form.addEventListener('submit', function(e) {
            e.preventDefault()
            nextStep(5)
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