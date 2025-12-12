/**
 * Візуалізатор графів для редактора
 */

let network = null;
let nodes = null;
let edges = null;
let nodeCounter = 0;
let edgeCounter = 0;
let selectedNodes = [];
let currentGraphId = null;

// Ініціалізація при завантаженні
$(document).ready(function() {
    initializeGraph();
    setupEventHandlers();
    updateEdgeWeightVisibility();
});

/**
 * Ініціалізація графа
 */
function initializeGraph() {
    const container = document.getElementById('graph-container');
    
    nodes = new vis.DataSet([]);
    edges = new vis.DataSet([]);
    
    const data = { nodes, edges };
    
    const options = {
        physics: false,
        manipulation: false,
        interaction: {
            dragNodes: true,
            dragView: true,
            zoomView: true
        },
        nodes: {
            shape: 'dot',
            size: 20,
            font: {
                size: 16,
                color: '#ffffff'
            },
            borderWidth: 2,
            color: {
                border: '#2B7CE9',
                background: '#97C2FC',
                highlight: {
                    border: '#2B7CE9',
                    background: '#D2E5FF'
                }
            }
        },
        edges: {
            width: 2,
            color: { color: '#848484' },
            smooth: {
                type: 'continuous'
            },
            font: {
                size: 14,
                align: 'top'
            }
        }
    };
    
    network = new vis.Network(container, data, options);
    
    // Події
    network.on('click', handleCanvasClick);
    network.on('doubleClick', handleDoubleClick);
    
    updateCounts();
}

/**
 * Налаштування обробників подій
 */
function setupEventHandlers() {
    // Зміна режиму
    $('#edit-mode').on('change', function() {
        selectedNodes = [];
        updateEdgeWeightVisibility();
    });
    
    // Слайдери параметрів (не використовується тут, але може бути корисно)
    $('.form-range').on('input', function() {
        const valueId = $(this).attr('id') + '-value';
        $('#' + valueId).text($(this).val());
    });
    
    // Збереження графа
    $('#save-graph').on('click', saveGraph);
    
    // Завантаження графа
    $('#load-graph').on('click', showLoadModal);
    
    // Очищення графа
    $('#clear-graph').on('click', clearGraph);
    
    // Генерація випадкового графа
    $('#generate-random').on('click', generateRandomGraph);
    
    // Генерація графа міст
    $('#generate-cities').on('click', generateCitiesGraph);
}

/**
 * Показати/сховати поле ваги ребра
 */
function updateEdgeWeightVisibility() {
    const mode = $('#edit-mode').val();
    if (mode === 'add-edge') {
        $('#edge-weight-group').show();
    } else {
        $('#edge-weight-group').hide();
    }
}

/**
 * Обробка кліку по полотну
 */
function handleCanvasClick(params) {
    const mode = $('#edit-mode').val();
    
    if (mode === 'add-node') {
        if (params.nodes.length === 0) {
            addNode(params.pointer.canvas);
        }
    } else if (mode === 'add-edge') {
        if (params.nodes.length > 0) {
            handleEdgeSelection(params.nodes[0]);
        }
    } else if (mode === 'delete') {
        if (params.nodes.length > 0) {
            deleteNode(params.nodes[0]);
        } else if (params.edges.length > 0) {
            deleteEdge(params.edges[0]);
        }
    }
}

/**
 * Обробка подвійного кліку
 */
function handleDoubleClick(params) {
    if (params.nodes.length > 0) {
        editNode(params.nodes[0]);
    } else if (params.edges.length > 0) {
        editEdge(params.edges[0]);
    }
}

/**
 * Додавання вершини
 */
function addNode(position) {
    const nodeId = 'node_' + nodeCounter++;
    const label = prompt('Введіть назву вершини:', 'V' + nodeCounter);
    
    if (label !== null && label.trim() !== '') {
        nodes.add({
            id: nodeId,
            label: label.trim(),
            x: position.x,
            y: position.y
        });
        
        updateCounts();
        showSuccess('Вершину додано');
    }
}

/**
 * Редагування вершини
 */
function editNode(nodeId) {
    const node = nodes.get(nodeId);
    const newLabel = prompt('Нова назва вершини:', node.label);
    
    if (newLabel !== null && newLabel.trim() !== '') {
        nodes.update({
            id: nodeId,
            label: newLabel.trim()
        });
        showSuccess('Вершину оновлено');
    }
}

/**
 * Видалення вершини
 */
function deleteNode(nodeId) {
    if (confirm('Видалити вершину?')) {
        nodes.remove(nodeId);
        updateCounts();
        showSuccess('Вершину видалено');
    }
}

/**
 * Вибір вершин для ребра
 */
function handleEdgeSelection(nodeId) {
    selectedNodes.push(nodeId);
    
    if (selectedNodes.length === 2) {
        const weight = parseFloat($('#edge-weight').val());
        addEdge(selectedNodes[0], selectedNodes[1], weight);
        selectedNodes = [];
    }
}

/**
 * Додавання ребра
 */
function addEdge(from, to, weight) {
    if (from === to) {
        showError('Не можна з\'єднати вершину саму з собою');
        return;
    }
    
    // Перевірка чи ребро вже існує
    const existingEdges = edges.get({
        filter: function(edge) {
            return (edge.from === from && edge.to === to) ||
                   (edge.from === to && edge.to === from);
        }
    });
    
    if (existingEdges.length > 0) {
        showError('Ребро вже існує');
        return;
    }
    
    const edgeId = 'edge_' + edgeCounter++;
    edges.add({
        id: edgeId,
        from: from,
        to: to,
        label: String(weight)
    });
    
    updateCounts();
    showSuccess('Ребро додано');
}

/**
 * Редагування ребра
 */
function editEdge(edgeId) {
    const edge = edges.get(edgeId);
    const newWeight = prompt('Нова вага ребра:', edge.label);
    
    if (newWeight !== null && !isNaN(newWeight) && parseFloat(newWeight) > 0) {
        edges.update({
            id: edgeId,
            label: String(parseFloat(newWeight))
        });
        showSuccess('Ребро оновлено');
    }
}

/**
 * Видалення ребра
 */
function deleteEdge(edgeId) {
    if (confirm('Видалити ребро?')) {
        edges.remove(edgeId);
        updateCounts();
        showSuccess('Ребро видалено');
    }
}

/**
 * Оновлення лічильників
 */
function updateCounts() {
    $('#node-count').text(nodes.length);
    $('#edge-count').text(edges.length);
}

/**
 * Збереження графа
 */
function saveGraph() {
    const graphName = $('#graph-name').val().trim();
    
    if (!graphName) {
        showError('Введіть назву графа');
        return;
    }
    
    if (nodes.length < 2) {
        showError('Граф повинен містити принаймні 2 вершини');
        return;
    }
    
    const graphData = {
        name: graphName,
        nodes: nodes.get().map(node => ({
            id: node.id,
            label: node.label,
            x: node.x,
            y: node.y
        })),
        edges: edges.get().map(edge => ({
            from: edge.from,
            to: edge.to,
            weight: parseFloat(edge.label)
        }))
    };
    
    const url = currentGraphId ? 
        `/api/graph/${currentGraphId}` : 
        '/api/graph/create';
    const method = currentGraphId ? 'PUT' : 'POST';
    
    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(graphData),
        success: function(response) {
            showSuccess('Граф збережено');
            if (!currentGraphId) {
                currentGraphId = response.graph_id;
            }
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Помилка збереження';
            showError(error);
        }
    });
}

/**
 * Показ модалки завантаження
 */
function showLoadModal() {
    $('#loadGraphModal').modal('show');
    loadGraphsList();
}

/**
 * Завантаження списку графів
 */
function loadGraphsList() {
    $('#graphs-list').html('<div class="text-center"><div class="spinner-border text-primary"></div></div>');
    
    $.get('/api/graph/all', function(data) {
        if (data.graphs.length === 0) {
            $('#graphs-list').html('<p class="text-muted">Немає збережених графів</p>');
            return;
        }
        
        let html = '<div class="list-group">';
        data.graphs.forEach(graph => {
            html += `
                <button class="list-group-item list-group-item-action" 
                        onclick="loadGraph('${graph._id}')">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">${graph.name}</h6>
                        <small class="text-muted">
                            ${graph.nodes.length} вершин, ${graph.edges.length} ребер
                        </small>
                    </div>
                </button>
            `;
        });
        html += '</div>';
        
        $('#graphs-list').html(html);
    }).fail(function() {
        showError('Помилка завантаження списку графів');
    });
}

/**
 * Завантаження графа
 */
function loadGraph(graphId) {
    $.get(`/api/graph/${graphId}`, function(data) {
        // Очищення поточного графа
        nodes.clear();
        edges.clear();
        
        // Завантаження даних
        $('#graph-name').val(data.name);
        currentGraphId = data._id;
        
        // Додавання вершин
        data.nodes.forEach(node => {
            nodes.add(node);
        });
        
        // Додавання ребер
        data.edges.forEach((edge, idx) => {
            edges.add({
                id: 'edge_' + idx,
                from: edge.from,
                to: edge.to,
                label: String(edge.weight)
            });
        });
        
        // Оновлення лічильників
        nodeCounter = nodes.length;
        edgeCounter = edges.length;
        updateCounts();
        
        // Закриття модалки
        $('#loadGraphModal').modal('hide');
        showSuccess('Граф завантажено');
        
    }).fail(function() {
        showError('Помилка завантаження графа');
    });
}

/**
 * Очищення графа
 */
function clearGraph() {
    if (confirm('Очистити граф? Всі незбережені дані будуть втрачені.')) {
        nodes.clear();
        edges.clear();
        nodeCounter = 0;
        edgeCounter = 0;
        currentGraphId = null;
        $('#graph-name').val('Новий граф');
        updateCounts();
        showSuccess('Граф очищено');
    }
}

/**
 * Генерація випадкового графа
 */
function generateRandomGraph() {
    // --- ВИПРАВЛЕННЯ: Змінено діапазон вершин на більший для демонстрації алгоритмів ---
    const numNodes = parseInt(prompt('Кількість вершин (20-50):', '30'));
    
    if (isNaN(numNodes) || numNodes < 20 || numNodes > 50) {
        showError('Введіть число від 20 до 50');
        return;
    }
    
    $.ajax({
        url: '/api/graph/generate/random',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ num_nodes: numNodes, connectivity: 0.3 }),
        success: function(response) {
            loadGraphData(response.graph);
            showSuccess('Випадковий граф згенеровано');
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Помилка генерації графа';
            showError(error);
        }
    });
}

/**
 * Генерація графа міст
 */
function generateCitiesGraph() {
    $.ajax({
        url: '/api/graph/generate/cities',
        method: 'POST',
        contentType: 'application/json',
        success: function(response) {
            loadGraphData(response.graph);
            showSuccess('Граф міст згенеровано');
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Помилка генерації графа міст';
            showError(error);
        }
    });
}

/**
 * Завантаження даних графа
 */
function loadGraphData(graphData) {
    nodes.clear();
    edges.clear();
    
    $('#graph-name').val(graphData.name);
    
    graphData.nodes.forEach(node => {
        nodes.add(node);
    });
    
    graphData.edges.forEach((edge, idx) => {
        edges.add({
            id: 'edge_' + idx,
            from: edge.from,
            to: edge.to,
            label: String(edge.weight)
        });
    });
    
    nodeCounter = nodes.length;
    edgeCounter = edges.length;
    updateCounts();
}

/**
 * Повідомлення
 */
function showSuccess(message) {
    showAlert(message, 'success');
}

function showError(message) {
    showAlert(message, 'danger');
}

function showAlert(message, type) {
    const alert = $(`
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
             style="top: 80px; right: 20px; z-index: 9999;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(alert);
    
    setTimeout(() => {
        alert.alert('close');
    }, 3000);
}