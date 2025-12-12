/**
 * Скрипт для сторінки пошуку шляхів
 */

let network = null;
let currentGraph = null;
let convergenceChart = null;

$(document).ready(function() {
    initializeSearch();
    setupEventHandlers();
});

/**
 * Ініціалізація
 */
function initializeSearch() {
    // Ініціалізація візуалізації
    const container = document.getElementById('graph-display');
    
    const data = {
        nodes: new vis.DataSet([]),
        edges: new vis.DataSet([])
    };
    
    const options = {
        physics: false,
        nodes: {
            shape: 'dot',
            size: 20,
            font: { size: 16, color: '#ffffff' }
        },
        edges: {
            width: 2,
            smooth: { type: 'continuous' },
            font: { size: 14, align: 'top' }
        }
    };
    
    network = new vis.Network(container, data, options);
}

/**
 * Налаштування обробників подій
 */
function setupEventHandlers() {
    // Вибір графа
    $('#graph-select').on('change', loadSelectedGraph);
    
    // Алгоритм
    $('input[name="algorithm"]').on('change', toggleACOParameters);
    
    // Слайдери параметрів
    $('#num-ants').on('input', function() {
        $('#ants-value').text($(this).val());
    });
    
    $('#alpha').on('input', function() {
        $('#alpha-value').text($(this).val());
    });
    
    $('#beta').on('input', function() {
        $('#beta-value').text($(this).val());
    });
    
    $('#evaporation').on('input', function() {
        $('#evap-value').text($(this).val());
    });
    
    $('#iterations').on('input', function() {
        $('#iter-value').text($(this).val());
    });
    
    // Кнопка пошуку
    $('#search-btn').on('click', runSearch);
}

/**
 * Показати/сховати параметри ACO
 */
function toggleACOParameters() {
    const algorithm = $('input[name="algorithm"]:checked').val();
    if (algorithm === 'ACO' || algorithm === 'Compare') {
        $('#aco-parameters').show();
    } else {
        $('#aco-parameters').hide();
    }
}

/**
 * Завантаження вибраного графа
 */
function loadSelectedGraph() {
    const graphId = $('#graph-select').val();
    
    if (!graphId) {
        $('#start-node, #end-node').prop('disabled', true).html('<option value="">-- Оберіть графа --</option>');
        $('#search-btn').prop('disabled', true);
        return;
    }
    
    $.get(`/api/graph/${graphId}`, function(graph) {
        currentGraph = graph;
        
        // Оновлення списків вершин
        let options = '<option value="">-- Оберіть вершину --</option>';
        graph.nodes.forEach(node => {
            options += `<option value="${node.id}">${node.label}</option>`;
        });
        
        $('#start-node, #end-node').prop('disabled', false).html(options);
        
        // Відображення графа
        displayGraph(graph);
        
        // Активація кнопки після вибору вершин
        $('#start-node, #end-node').off('change').on('change', function() {
            const start = $('#start-node').val();
            const end = $('#end-node').val();
            $('#search-btn').prop('disabled', !(start && end && start !== end));
        });
        
    }).fail(function() {
        alert('Помилка завантаження графа');
    });
}

/**
 * Відображення графа
 */
function displayGraph(graph) {
    const nodes = new vis.DataSet(graph.nodes);
    const edges = new vis.DataSet(graph.edges.map((edge, idx) => ({
        id: idx,
        from: edge.from,
        to: edge.to,
        label: String(edge.weight)
    })));
    
    network.setData({ nodes, edges });
}

/**
 * Виконання пошуку
 */
function runSearch() {
    const graphId = $('#graph-select').val();
    const algorithm = $('input[name="algorithm"]:checked').val();
    const start = $('#start-node').val();
    const end = $('#end-node').val();
    
    // Валідація
    if (!graphId || !start || !end) {
        alert('Оберіть граф та вершини');
        return;
    }
    
    if (start === end) {
        alert('Початкова та кінцева вершини повинні відрізнятися');
        return;
    }
    
    // Підготовка параметрів
    const parameters = {
        num_ants: parseInt($('#num-ants').val()),
        alpha: parseFloat($('#alpha').val()),
        beta: parseFloat($('#beta').val()),
        evaporation: parseFloat($('#evaporation').val()),
        iterations: parseInt($('#iterations').val())
    };
    
    // Показ індикатора
    $('#results-container').hide();
    $('#loading-indicator').show();
    $('#search-btn').prop('disabled', true);
    
    if (algorithm === 'Compare') {
        runComparison(graphId, start, end, parameters);
    } else {
        runSingleAlgorithm(graphId, algorithm, start, end, parameters);
    }
}

/**
 * Виконання одного алгоритму
 */
function runSingleAlgorithm(graphId, algorithm, start, end, parameters) {
    $.ajax({
        url: '/api/search/run',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            graph_id: graphId,
            algorithm: algorithm,
            start: start,
            end: end,
            parameters: parameters
        }),
        success: function(result) {
            displaySingleResult(result);
        },
        error: function(xhr) {
            alert('Помилка пошуку: ' + (xhr.responseJSON?.error || 'Unknown error'));
        },
        complete: function() {
            $('#loading-indicator').hide();
            $('#search-btn').prop('disabled', false);
        }
    });
}

/**
 * Порівняння алгоритмів
 */
function runComparison(graphId, start, end, parameters) {
    $.ajax({
        url: '/api/search/compare',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            graph_id: graphId,
            start: start,
            end: end,
            aco_parameters: parameters
        }),
        success: function(data) {
            displayComparisonResults(data);
        },
        error: function(xhr) {
            alert('Помилка порівняння: ' + (xhr.responseJSON?.error || 'Unknown error'));
        },
        complete: function() {
            $('#loading-indicator').hide();
            $('#search-btn').prop('disabled', false);
        }
    });
}

/**
 * Відображення результату одного алгоритму
 */
function displaySingleResult(result) {
    $('#results-container').show();
    
    if (result.algorithm === 'ACO') {
        displayACOResult(result);
        $('#aco-result').show();
        $('#dijkstra-result').hide();
    } else {
        displayDijkstraResult(result);
        $('#dijkstra-result').show();
        $('#aco-result').hide();
    }
    
    $('#comparison-result').hide();
    
    // Підсвічування шляху
    highlightPath(result.path);
}

/**
 * Відображення результату ACO
 */
function displayACOResult(result) {
    $('#aco-distance').text(result.distance ? result.distance.toFixed(2) : '∞');
    $('#aco-time').text(result.execution_time.toFixed(6));
    $('#aco-iterations').text(result.iterations);
    
    const pathHtml = result.path.map((node, idx) => {
        let badgeClass = 'secondary';
        if (idx === 0) badgeClass = 'primary';
        if (idx === result.path.length - 1) badgeClass = 'danger';
        return `<span class="badge bg-${badgeClass} me-1">${node}</span>`;
    }).join('<i class="bi bi-arrow-right text-muted"></i>');
    
    $('#aco-path').html(pathHtml);
    
    // Графік збіжності
    if (result.history && result.history.length > 0) {
        displayConvergenceChart(result.history);
    }
}

/**
 * Відображення результату Dijkstra
 */
function displayDijkstraResult(result) {
    $('#dijkstra-distance').text(result.distance ? result.distance.toFixed(2) : '∞');
    $('#dijkstra-time').text(result.execution_time.toFixed(6));
    
    const pathHtml = result.path.map((node, idx) => {
        let badgeClass = 'secondary';
        if (idx === 0) badgeClass = 'primary';
        if (idx === result.path.length - 1) badgeClass = 'danger';
        return `<span class="badge bg-${badgeClass} me-1">${node}</span>`;
    }).join('<i class="bi bi-arrow-right text-muted"></i>');
    
    $('#dijkstra-path').html(pathHtml);
}

/**
 * Відображення порівняння
 */
function displayComparisonResults(data) {
    $('#results-container').show();
    $('#aco-result').show();
    $('#dijkstra-result').show();
    $('#comparison-result').show();
    
    displayACOResult(data.aco);
    displayDijkstraResult(data.dijkstra);
    
    // Таблиця порівняння
    $('#comp-aco-dist').text(data.aco.distance ? data.aco.distance.toFixed(2) : '∞');
    $('#comp-dijk-dist').text(data.dijkstra.distance ? data.dijkstra.distance.toFixed(2) : '∞');
    
    if (data.comparison.distance_difference !== null) {
        $('#comp-dist-diff').text(data.comparison.distance_difference.toFixed(2));
    } else {
        $('#comp-dist-diff').text('N/A');
    }
    
    $('#comp-aco-time').text(data.aco.execution_time.toFixed(6) + ' с');
    $('#comp-dijk-time').text(data.dijkstra.execution_time.toFixed(6) + ' с');
    $('#comp-time-diff').text(data.comparison.time_difference.toFixed(6) + ' с');
    
    const samePath = data.comparison.same_path ? 
        '<span class="badge bg-success">Так</span>' : 
        '<span class="badge bg-warning">Ні</span>';
    $('#comp-same-path').html(samePath);

    // Підсвічування шляху (використовуємо результат Дейкстри, оскільки він точний)
    highlightPath(data.dijkstra.path);
}

// --- ВИПРАВЛЕННЯ: Додано відсутні функції для логіки фронтенду ---

/**
 * Підсвічує знайдений шлях на графі
 */
function highlightPath(path) {
    // Скидання всіх стилів
    const nodesToReset = network.body.data.nodes.map(node => ({
        id: node.id,
        color: '#97C2FC', // Повертаємо початковий колір
        size: 20
    }));
    network.body.data.nodes.update(nodesToReset);


    const edgesToReset = network.body.data.edges.map(edge => ({
        id: edge.id,
        color: '#848484', // Повертаємо початковий колір
        width: 2
    }));
    network.body.data.edges.update(edgesToReset);
    

    const edgesUpdate = currentGraph.edges.map((edge, idx) => {
        const inPath = path.some((node, i) =>
            i < path.length - 1 &&
            ((path[i] === edge.from && path[i+1] === edge.to) ||
             (path[i] === edge.to && path[i+1] === edge.from))
        );

        // Якщо ребро знайдено у шляху
        if (inPath) {
            return {
                id: edgesToReset[idx].id, // Використовуємо оригінальний id з Vis.js
                color: '#198754', // Зелений для шляху
                width: 4
            };
        }
        return null;
    }).filter(e => e !== null);

    if (edgesUpdate.length > 0) {
        network.body.data.edges.update(edgesUpdate);
    }
    
    // Підсвічування вершин
    path.forEach((nodeId, idx) => {
        let color = '#198754'; // Колір шляху
        if (idx === 0) color = '#0d6efd'; // Старт: синій
        if (idx === path.length - 1) color = '#dc3545'; // Кінець: червоний

        network.body.data.nodes.update({
            id: nodeId,
            color: { background: color, border: color },
            size: 25
        });
    });
}

/**
 * Відображення графіка збіжності ACO
 */
function displayConvergenceChart(history) {
    const ctx = document.getElementById('aco-convergence').getContext('2d');
    
    // Знищення попереднього графіка
    if (convergenceChart) {
        convergenceChart.destroy();
    }
    
    const labels = history.map(h => h.iteration);
    const data = history.map(h => h.best_distance);
    
    convergenceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Найкраща відстань',
                data: data,
                borderColor: 'rgba(25, 135, 84, 1)', // success-color
                backgroundColor: 'rgba(25, 135, 84, 0.2)',
                borderWidth: 2,
                pointRadius: 3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: { display: true, text: 'Ітерація' }
                },
                y: {
                    title: { display: true, text: 'Відстань' },
                    beginAtZero: true
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}