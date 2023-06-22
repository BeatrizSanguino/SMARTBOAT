let mqtt;
let reconnectTimeout = 2000;
let host = "broker.hivemq.com";
let port = 8000;
let tt =500;
let M1 =0;
let M2 = 0;
let res = {x:0,y:0};
let d = 0;
// Declare a global array to store all the distances
let distances = [];
let count_graph = 0;
let cnt = 0;
let y_range = [];
//document.getElementById("coord").innerHTML = result

function onConnect() {
    // Once a connection has been made, make a subscription and send a message.

    console.log("Connected ");
    mqtt.subscribe("robot/sensor_distance",{qos: 2});
    mqtt.subscribe("robot/GPS_position",{qos: 2});
    //message = new Paho.MQTT.Message("connected");
    //message.destinationName = "robot/motor_action";
    //mqtt.send(message);

}
function onMessageArrived(message) {
    // Extract the topic and payload from the incoming message
    var topic = message.destinationName;
    var payload = message.payloadString;

    // Log the payload for debugging purposes
    console.log(message.payloadString)
    
    if (topic=="robot/sensor_distance"){
        distance = parseFloat(payload)
        console.log(distance)
        
        // Append the distance value to the global array
        distances.push(distance);
        
        // Calculate the range of the y-axis
        //let y_range = [Math.min(...distances) * 0.9, Math.max(...distances) * 1.1];

        Plotly.extendTraces('graph', {
            x: [[count_graph]],
            y: [[distance]]
        }, [0]);

        // Update the range of the y-axis if more than 30 data points have been received
        if (cnt > 30) {
            y_range = [Math.min(...distances.slice(-30)) * 0.9, Math.max(...distances.slice(-30)) * 1.1];
            Plotly.relayout('graph', {
                xaxis: {range: [cnt-30, cnt]},
                yaxis: {range: y_range}
            });
        } else {
            Plotly.relayout('graph', {
                xaxis: {range: [0, cnt+1]},
                yaxis: {range: [Math.min(...distances) * 0.9, Math.max(...distances) * 1.1]}
            });
        }
        
        // Update the count of data points
        count_graph++;
        cnt++;  

    } else if (topic=="robot/GPS_position") {
        //position = payload;
        arr = str.split(", ");
        console.log(arr)

        result = arr[0] + "°, " + arr[1] + "°";
        document.getElementById("coord").innerHTML = result;
    }
    //let div = document.getElementById('output');
    //div.innerHTML += out_msg + "<br>"
    
}


function MQTTconnect() {
    console.log("connecting to " + host + " " + port);

    //let x = Math.floor(Math.random() * 10000);
    //let cname = "orderform-" + x;
    
    var client_id_name = "robot_controller".concat(Math.random().toString);

    mqtt = new Paho.MQTT.Client(host, port, client_id_name);

    let options = {
        timeout: 3,
        onSuccess: onConnect
    };

    mqtt.onMessageArrived = onMessageArrived

    mqtt.connect(options); //connect  
}

class JoystickController
{
	// adapted from: https://www.cssscript.com/touch-joystick-controller/#google_vignette
    // stickID: ID of HTML element (representing joystick) that will be dragged
	// maxDistance: maximum amount joystick can move in any direction
	// deadzone: joystick must move at least this amount from origin to register value change
	constructor( stickID, maxDistance, deadzone )
	{
		this.id = stickID;
		let stick = document.getElementById(stickID);

		// location from which drag begins, used to calculate offsets
		this.dragStart = null;

		// track touch identifier in case multiple joysticks present
		this.touchId = null;
		
		this.active = false;
		this.value = { x: 0, y: 0 }; 

		let self = this;

		function handleDown(event)
		{
		    self.active = true;

			// all drag movements are instantaneous
			stick.style.transition = '0s';

			// touch event fired before mouse event; prevent redundant mouse event from firing
			event.preventDefault();

		    if (event.changedTouches)
		    	self.dragStart = { x: event.changedTouches[0].clientX, y: event.changedTouches[0].clientY };
		    else
		    	self.dragStart = { x: event.clientX, y: event.clientY };

			// if this is a touch event, keep track of which one
		    if (event.changedTouches)
		    	self.touchId = event.changedTouches[0].identifier;
		}
		
		function handleMove(event) 
		{
		    if ( !self.active ) return;

		    // if this is a touch event, make sure it is the right one
		    // also handle multiple simultaneous touchmove events
		    let touchmoveId = null;
		    if (event.changedTouches)
		    {
		    	for (let i = 0; i < event.changedTouches.length; i++)
		    	{
		    		if (self.touchId == event.changedTouches[i].identifier)
		    		{
		    			touchmoveId = i;
		    			event.clientX = event.changedTouches[i].clientX;
		    			event.clientY = event.changedTouches[i].clientY;
		    		}
		    	}

		    	if (touchmoveId == null) return;
		    }

		    const xDiff = event.clientX - self.dragStart.x;
		    const yDiff = event.clientY - self.dragStart.y;
		    const angle = Math.atan2(yDiff, xDiff);
			const distance = Math.min(maxDistance, Math.hypot(xDiff, yDiff));
			const xPosition = distance * Math.cos(angle);
			const yPosition = distance * Math.sin(angle);

			// move stick image to new position
		    stick.style.transform = `translate3d(${xPosition}px, ${yPosition}px, 0px)`;

			// deadzone adjustment
			const distance2 = (distance < deadzone) ? 0 : maxDistance / (maxDistance - deadzone) * (distance - deadzone);
		    const xPosition2 = distance2 * Math.cos(angle);
			const yPosition2 = distance2 * Math.sin(angle);
		    const xPercent = parseFloat((xPosition2 / maxDistance).toFixed(4));
		    const yPercent = parseFloat((yPosition2 / maxDistance).toFixed(4));
		    
		    self.value = { x: xPercent, y: yPercent };

            var now = new Date();
            
            if ((now-t0)*0.001>1/freq){
                var res = coord2motor(parseFloat(self.value.x),parseFloat(self.value.y));
                var M1_string = res.M1.toString();
                var M2_string = res.M2.toString();
                var message_content = M1_string.concat(',',M2_string)
                var message = new Paho.MQTT.Message(message_content);
                message.destinationName = "robot/motor_action";
                message.qos = 2;
                message.retained = false;
                mqtt.send(message);
                console.log(message_content);
                console.log(message);
                t0 = new Date()}
            
		  }

		function handleUp(event) 
		{
		    if ( !self.active ) return;

		    // if this is a touch event, make sure it is the right one
		    if (event.changedTouches && self.touchId != event.changedTouches[0].identifier) return;

		    // transition the joystick position back to center
		    stick.style.transition = '.2s';
		    stick.style.transform = `translate3d(0px, 0px, 0px)`;

		    // reset everything
		    self.value = { x: 0, y: 0 };
		    self.touchId = null;
		    self.active = false;

            var res = coord2motor(parseFloat(self.value.x),parseFloat(self.value.y));
            var M1_string = res.M1.toString();
            var M2_string = res.M2.toString();
            var message_content = M1_string.concat(',',M2_string)
            var message = new Paho.MQTT.Message(message_content);
            message.destinationName = "robot/motor_action";
            message.qos = 2;
            message.retained = false;
            mqtt.send(message);
            console.log(message_content);
            console.log(message);

            
		}

        function coord2motor(x,y)
        {
            if (x<0 && y>=0 ){
                var d = Math.sqrt(Math.abs(x)**2 + Math.abs(y)**2)
                var alpha=Math.atan2(Math.abs(x),y);
                var M2 = d*( -(2/(Math.PI/2))*alpha + 1);
                var M1 = d*(1);
            }
            else if (x>0 && y<=0){
                var d = Math.sqrt(Math.abs(x)**2 + Math.abs(y)**2)
                var alpha=Math.atan2(Math.abs(y), x);
                var M2 = d*(-(2/(Math.PI/2))*alpha + 1);
                var M1 = d*(-1);
            }
            else if (x>=0 && y>0){
                var d = Math.sqrt(Math.abs(x)**2 + Math.abs(y)**2)
                var alpha=Math.atan2(y, x);
                var M1 = d*((2/(Math.PI/2))*alpha - 1);
                var M2=d*(1);
            }
            else if (x<=0 && y<0){
                var d = Math.sqrt(Math.abs(x)**2 + Math.abs(y)**2)
                var alpha=Math.atan2(Math.abs(y), Math.abs(x));
                var M1 = d*((2/(Math.PI/2))*alpha - 1);
                var M2=d*(-1);
            }
            else if (x==0 && y==0){
                var alpha = 0;
                var M2=0;
                var M1=0;
            }
            return { M1: M1, M2: M2 }
        }

		stick.addEventListener('mousedown', handleDown);
		stick.addEventListener('touchstart', handleDown);
		document.addEventListener('mousemove', handleMove, {passive: false});
		document.addEventListener('touchmove', handleMove, {passive: false});
		document.addEventListener('mouseup', handleUp);
		document.addEventListener('touchend', handleUp);
	}
}


var t0 = new Date()
var freq = 10

let joystick1 = new JoystickController("stick1", 128, 8);

//function update()
//{
//	document.getElementById("status1").innerText = "Joystick 1: " + JSON.stringify(joystick1.value);
//}

function loop()
{
	requestAnimationFrame(loop);
	//update();
}

let position;

MQTTconnect()

var distance
var trace = {x: [],y: [],mode: 'lines'};
  
var layout = {
    title: 'Measurement from the distance sensor',
    xaxis: {title: 'Iteration number'},
    yaxis: {title: 'Distance [m]'}};

Plotly.newPlot('graph', [trace], layout);

loop();


