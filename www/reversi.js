"use strict";

var url = "ws://127.0.0.1:8888/ws";

var cells = [];
var playerCell = null;
var webSocket = null;

var initView = function initView(size) {
    var board = document.getElementById("board");
    var cell = document.getElementById("cell");
    var indicator = document.getElementById("indicator");
    var row = document.getElementById("row");

    for (var y = -1; y < size; y++) {
        var r = row.cloneNode(true);
        for (var x = -1; x < size; x++) {
            var c = null;
            if (x == -1 && y == -1) {
                c = cell.cloneNode(true);
                playerCell = c;
            } else if (x == -1) {
                c = indicator.cloneNode(true);
                c.textContent = "12345678".charAt(y);
            } else if (y == -1) {
                c = indicator.cloneNode(true);
                c.textContent = "ABCDEFGH".charAt(x);
            } else {
                (function () {
                    c = cell.cloneNode(true);
                    var _x = x;
                    var _y = y;
                    c.onclick = function () {
                        handleClick(_x, _y);
                    };
                    cells.push(c);
                })();
            }
            r.appendChild(c);
        }
        board.appendChild(r);
    }
};

var updateView = function updateView(player, board) {
    updateCell(playerCell, player);
    board.forEach(function (v, i) {
        updateCell(cells[i], v);
    });
};

var updateCell = function updateCell(cell, player) {
    if (player == 0) {
        cell.className = "cell";
    } else if (player == -1) {
        cell.className = "cell white";
    } else {
        cell.className = "cell black";
    }
};

var updateAIList = function updateAIList(ai) {
    var select = document.getElementById("ai");
    console.log(ai);
    var _iteratorNormalCompletion = true;
    var _didIteratorError = false;
    var _iteratorError = undefined;

    try {
        for (var _iterator = select.options[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
            var child = _step.value;

            console.log(child);
            if (ai.indexOf(child.value) == -1) {
                select.removeChild(child);
            }
        }
    } catch (err) {
        _didIteratorError = true;
        _iteratorError = err;
    } finally {
        try {
            if (!_iteratorNormalCompletion && _iterator.return) {
                _iterator.return();
            }
        } finally {
            if (_didIteratorError) {
                throw _iteratorError;
            }
        }
    }
};

var handle = function handle(event) {
    if (event && event.data) {
        var json = JSON.parse(event.data);
        var command = json.command;

        console.log(json);

        switch (command) {
            case "init":
                initView(json.size);
                updateAIList(json.ai);
                break;
            case "update":
                updateView(json.player, json.board);
                break;
            case "judge":
                if (json.winner == -1) {
                    alert("White won.");
                } else if (json.winner == 1) {
                    alert("Black won.");
                } else {
                    alert("Draw.");
                }
                break;
            case "error":
                console.log("error:", json["message"]);
                break;
            default:
                console.log("invalid command:", command);
                break;
        }
    }
};

var handleClick = function handleClick(x, y) {
    var json = { command: "put", position: [x, y] };

    webSocket.send(JSON.stringify(json));
};

onload = function onload() {

    webSocket = new WebSocket(url);
    webSocket.onopen = function () {
        console.log("WebSocket Opened.");
    };
    webSocket.onmessage = handle;
    webSocket.onclose = function () {
        alert("WebSocket Closed.");
        console.log("WebSocket Closed.");
    };
    webSocket.onerror = function (event) {
        console.log("error:" + event);
    };

    document.getElementById("ai").onchange = function () {
        var ai = document.getElementById("ai").value;
        var json = { command: "ai", "ai": ai };
        webSocket.send(JSON.stringify(json));
    };

    var restart = function restart(side) {
        return function () {
            var json = { command: "restart", "side": side };
            webSocket.send(JSON.stringify(json));
        };
    };
    document.getElementById("restart_black").onclick = restart(1);
    document.getElementById("restart_white").onclick = restart(-1);
};