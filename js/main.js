"use strict"

const url = "ws://127.0.0.1:8888/ws";

const cells = [];
let playerCell = null;
let webSocket = null;

const initView = (size)=>{
    const board = document.getElementById("board");
    const cell = document.getElementById("cell");
    const indicator = document.getElementById("indicator");
    const row = document.getElementById("row");
    
    for(let y = -1 ; y < size ; y++) {
        let r = row.cloneNode(true);
        for(let x = -1 ; x < size ; x++) {
            var c = null;
            if(x == -1 && y == -1) {
                c = cell.cloneNode(true);
                playerCell = c;
            } else if(x == -1) {
                c = indicator.cloneNode(true);
                c.textContent = "12345678".charAt(y);
            } else if(y == -1) {
                c = indicator.cloneNode(true);
                c.textContent = "ABCDEFGH".charAt(x);
            } else {
                c = cell.cloneNode(true);
                const _x = x;
                const _y = y;
                c.onclick = ()=>{
                  handleClick(_x,_y);
                }
                cells.push(c);
            }
            r.appendChild(c);
        }
        board.appendChild(r);
    }
};

const updateView = (player, board)=>{
    updateCell(playerCell, player);
    board.forEach((v, i)=>{
        updateCell(cells[i], v);
    });
};

const updateCell = (cell, player)=>{
    if(player == 0) {
        cell.className = "cell";
    } else if(player == -1) {
        cell.className = "cell white";
    } else {
        cell.className = "cell black";
    }
};

const updateAIList = (ai)=>{
    const select = document.getElementById("ai");
    
    let removeList = []
    for(let child of select.options) {
        if(ai.indexOf(child.value) == -1) {
            removeList.push(child);
        }
    }
    for(let child of removeList) {
        select.removeChild(child);
    }
}

const handle = (event)=>{
    if(event && event.data){
        const json = JSON.parse(event.data);
        const command = json.command;
        
        console.log(json)
        
        switch(command){
            case "init":
                initView(json.size);
                updateAIList(json.ai);
                break;
            case "update":
                updateView(json.player, json.board);
                break;
            case "judge":
                if(json.winner == -1) {
                    alert("White won.");
                } else if(json.winner == 1) {
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

const handleClick = (x, y)=>{
    const json = {command: "put", position:[x,y]};
    
    webSocket.send(JSON.stringify(json));
};



onload = ()=>{
    
    webSocket = new WebSocket(url);
    webSocket.onopen = ()=>{
        console.log("WebSocket Opened.");
    };
    webSocket.onmessage = handle;
    webSocket.onclose = ()=>{
        alert("WebSocket Closed.")
        console.log("WebSocket Closed.");
    };
    webSocket.onerror = (event)=>{
        console.log("error:"+event);
    };
    
    document.getElementById("ai").onchange = ()=>{
        const ai = document.getElementById("ai").value;
        const json = {command: "ai", "ai":ai};
        webSocket.send(JSON.stringify(json));
    };
    
    const restart = (side)=>{
        return ()=>{
            const json = {command: "restart", "side":side};
            webSocket.send(JSON.stringify(json));
        };
    };
    document.getElementById("restart_black").onclick = restart(1);
    document.getElementById("restart_white").onclick = restart(-1);
};