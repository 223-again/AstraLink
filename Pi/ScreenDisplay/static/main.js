// WebSocket连接
let socket = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function initWebSocket() {
    try {
        socket = io();
        
        socket.on('connect', function() {
            console.log('WebSocket连接成功');
            reconnectAttempts = 0;
        });
        
        socket.on('disconnect', function() {
            console.log('WebSocket连接断开');
            setTimeout(initWebSocket, 2000);
        });
        
        // 实时传感器数据更新
        socket.on('sensor_update', function(data) {
            updateSensorDisplay(data);
        });
        
        // 实时表情更新
        socket.on('mood_update', function(data) {
            updateEmojiDisplay(data.mood);
        });
        
        // 实时对话更新
        socket.on('conversation_update', function(data) {
            updateConversationDisplay(data);
        });
        
        // 实时WiFi质量更新
        socket.on('wifi_update', function(data) {
            updateWifiDisplay(data.quality);
        });
        
        // 实时状态更新
        socket.on('status_update', function(data) {
            updateStatusDisplay(data.status);
        });
        
    } catch (error) {
        console.error('WebSocket初始化失败:', error);
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(initWebSocket, 2000);
        }
    }
}

function updateTime() {
    // 直接使用JavaScript获取本地时间，无需API调用
    const now = new Date();
    const timeString = now.toLocaleTimeString('zh-CN', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
    const dateString = now.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).replace(/\//g, '-');
    
    document.getElementById("time").innerText = timeString;
    document.getElementById("date").innerText = dateString;
}

function updateYiyan() {
    const yiyan = document.getElementById("yiyan");
    yiyan.classList.add("fade");
    setTimeout(() => {
        fetch("/api/yiyan")
            .then((r) => r.json())
            .then((d) => {
                yiyan.innerText = d.yiyan || "……";
                yiyan.classList.remove("fade");
                yiyan.style.opacity = 1;
            })
            .catch(() => {
                yiyan.innerText = "获取失败";
                yiyan.classList.remove("fade");
                yiyan.style.opacity = 1;
            });
    }, 400);
}

function updateEmoji() {
    fetch("/api/mood")
        .then((r) => r.json())
        .then((d) => {
            updateEmojiDisplay(d.mood);
        })
        .catch(error => {
            console.error('获取表情失败:', error);
        });
}

function updateEmojiDisplay(mood) {
    const emoji = document.getElementById("emoji");
    emoji.src = "/emoji/" + mood + ".gif";
    const box = document.querySelector(".emoji-box");
    box.classList.add("shake");
    setTimeout(() => box.classList.remove("shake"), 500);
}

function updateSensor() {
    fetch("/api/sensor")
        .then((r) => r.json())
        .then((d) => {
            updateSensorDisplay(d);
        })
        .catch(error => {
            console.error('获取传感器数据失败:', error);
            document.getElementById("temperature").textContent = "--";
            document.getElementById("humidity").textContent = "--";
        });
}

function updateSensorDisplay(data) {
    if (data.temperature !== undefined && data.humidity !== undefined) {
        document.getElementById("temperature").textContent = data.temperature;
        document.getElementById("humidity").textContent = data.humidity;
        
        // 添加数据更新动画
        const tempElement = document.getElementById("temperature");
        const humElement = document.getElementById("humidity");
        tempElement.classList.add("data-update");
        humElement.classList.add("data-update");
        setTimeout(() => {
            tempElement.classList.remove("data-update");
            humElement.classList.remove("data-update");
        }, 300);
    } else {
        document.getElementById("temperature").textContent = "--";
        document.getElementById("humidity").textContent = "--";
    }
}

function updateConversationDisplay(data) {
    // 更新对话显示逻辑
    if (data.message && data.response) {
        // 这里可以添加对话显示的具体逻辑
        console.log('对话更新:', data);
    }
}

function updateWifiDisplay(quality) {
    // 更新WiFi质量显示逻辑
    console.log('WiFi质量更新:', quality);
}

function updateStatusDisplay(status) {
    // 更新状态显示逻辑
    console.log('状态更新:', status);
}

function forceUpdateSensor() {
    // 强制更新传感器数据
    if (socket && socket.connected) {
        socket.emit('request_update');
    } else {
        fetch("/api/sensor/force_update")
            .then((r) => r.json())
            .then((d) => {
                updateSensorDisplay(d);
            })
            .catch(error => {
                console.error('强制更新传感器数据失败:', error);
            });
    }
}

function toggleFullScreen() {
    if (!document.fullscreenElement) document.documentElement.requestFullscreen();
    else document.exitFullscreen();
}

function getWeatherIcon(desc) {
    // 简单映射，可根据需要扩展
    if (desc.includes("晴")) return "☀️";
    if (desc.includes("多云")) return "⛅";
    if (desc.includes("阴")) return "☁️";
    if (desc.includes("雨")) return "🌧️";
    if (desc.includes("雪")) return "❄️";
    if (desc.includes("雾")) return "🌫️";
    return "🌡️";
}

function updateWeather() {
    fetch("https://v.api.aa1.cn/api/api-tianqi-3/index.php?msg=宁波&type=1")
        .then((r) => r.json())
        .then((d) => {
            if (d.code === "1" && d.data && d.data.length > 0) {
                const today = d.data[0];
                document.getElementById("weather-icon").textContent = getWeatherIcon(
                    today.tianqi
                );
                document.getElementById("weather-temp").textContent =
                    today.wendu + "°C";
                document.getElementById("weather-desc").textContent = "PM:" + today.pm;
            } else {
                document.getElementById("weather-icon").textContent = "❓";
                document.getElementById("weather-temp").textContent = "--°C";
                document.getElementById("weather-desc").textContent = "获取失败";
            }
        })
        .catch(() => {
            document.getElementById("weather-icon").textContent = "❓";
            document.getElementById("weather-temp").textContent = "--°C";
            document.getElementById("weather-desc").textContent = "获取失败";
        });
}

// 初始化WebSocket连接
initWebSocket();

// 优化后的定时刷新 - 减少轮询频率，依赖WebSocket实时更新
setInterval(updateTime, 1000);  // 时间每秒更新
setInterval(updateYiyan, 60000);  // 一言每分钟更新一次
setInterval(updateEmoji, 30000);  // 表情每30秒更新一次（作为WebSocket的备用）
setInterval(updateSensor, 10000);  // 传感器每10秒更新一次（作为WebSocket的备用）
setInterval(updateWeather, 30 * 60 * 1000);  // 天气半小时更新一次

// 首次加载
updateTime();
updateYiyan();
updateEmoji();
updateWeather();
updateSensor();

// 双击全屏
document.body.ondblclick = toggleFullScreen;

// 添加键盘快捷键
document.addEventListener('keydown', function(event) {
    switch(event.key) {
        case 'f':
        case 'F':
            toggleFullScreen();
            break;
        case 'r':
        case 'R':
            if (event.ctrlKey) {
                event.preventDefault();
                forceUpdateSensor();
            }
            break;
    }
});
