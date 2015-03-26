/**
 * Created by User on 5/7/14.
 */

function nodesCtrl($scope) {
	
	reset();

    function reset() {
        $scope.nodes = [];
        $scope.firstOrderWeights = []; // node,node -> val
        $scope.secondOrderWeights = [];// node,node , node,node -> val
        $scope.treeVal = 0.0;
        $scope.allEdges = [];
		$scope.edgesColors = [];
        $scope.randText = "";
        $('#graphCanvas')[0].getContext('2d').clearRect(0,0,$('#graphCanvas')[0].width,$('#graphCanvas')[0].height);
    }

    // $scope.nodes=[{text:"I",id:0},{text:"am",id:1},{text:"Ilan",id:2},{text: "ALongWordWithLotsOFText",id:3},{text:"anotherWord",id:4}];

    $('#inputFile')[0].onchange = function(e) {
        if (e.target.files.length > 0) {
			
            reset();
			handleChange(e.target.files[0]);
        }
    }

    $scope.updateCanvas = function(nodeId) {
        parentVal = $('#node' + nodeId).val();
        if (parseInt(parentVal) === nodeId) {
            return;
        }
        if (parentVal == "") {
            clearEdge(nodeId,$scope.selectedEdges[nodeId]);
        }
        else {
            parentNum = parseInt(parentVal);
            // in input is legal
            if ((parentNum >= 0) && (parentNum < $scope.nodes.length)) {
                // if there was a number there
                clearEdge(nodeId,parentNum);

                // add a new edge
                addEdge(nodeId,parentNum);
            }
            console.log('UC');
        }
    }
	
	function handleChange(infile) {
		// read input
		var fr = new FileReader();
		fr.readAsText(infile);
		fr.onload = function(e) {
			parseInputFile(e.target.result,$scope);
			$scope.$digest();
		};
	}
	
	function clearEdges(toList,fromList) {
		
		for (i = 0; i < toList.length ; i++) {
			if ($scope.allEdges[toList[i]][fromList[i]]) {
				$scope.allEdges[toList[i]][fromList[i]] = undefined;
				$scope.edgesColors[toList[i]][fromList[i]]   = undefined;
			}
		}
		
		// update score
        updateScores();

        // update canvas
        drawCanvas();
	}
	
    function clearEdge(nodeId,parentNum) {
		clearEdges([nodeId],[parentNum]);
    }
	
	function addEdges(toList,fromList,color) {
		for (i = 0; i < toList.length ; i++) {
			$scope.allEdges[toList[i]][fromList[i]] = 1;
			if (color) {
				$scope.edgesColors[toList[i]][fromList[i]] = color;
			}
		}
		// update scores
        updateScores();

        // update canvas
        drawCanvas();
        // digest?
	}

    function addEdge(nodeId,parentNum) {
		addEdges([nodeId],[parentNum]);
    }

    function updateScores(from,to,addedOrRemoved) {
        // run on all edges
		return;
        sum = 0.0;
        for (to1 in $scope.selectedEdges) {
            from1 = $scope.selectedEdges[to1];
            if (from1 >= 0) {
                sum += parseFloat($scope.firstOrderWeights[from1][to1]);
                for (to2= to1+1 ; to2 < $scope.selectedEdges.length ; to2++) {
                    from2 = $scope.selectedEdges[to2];
                    if (from2 >= 0) {
                        sum += parseFloat($scope.secondOrderWeights[from1][to1][from2][to2]);
                    }
                }
            }
        }
        $scope.treeVal = sum;
    }

    function drawCanvas() {
        var canvas = $('#graphCanvas')[0];
        canvas.width = canvas.offsetWidth;
        canvas.height = canvas.offsetHeight;
        var ctx = canvas.getContext('2d');
        ctx.clearRect(0,0,canvas.width,canvas.height); // clear canvas

        // arrow colors:
        colors = ["red","black","lime","brown", "darkBlue", "orange", "lawnGreen", "purple"];
        for (to = 0; to < $scope.allEdges.length; to++) {
            
			for (from = 0; from < $scope.allEdges[to].length; from++) {
				ctx.beginPath();
				if ($scope.allEdges[to][from]) {
					// find out where to put the arrows
					from_x  = $('#node' + from).parent()[0].offsetWidth/2; // middle of the word
					from_x += $('#node' + from).parent()[0].offsetLeft;
					from_x -= canvas.offsetLeft;

					to_x  = $('#node' + to).parent()[0].offsetWidth/2; // middle of the word
					to_x += $('#node' + to).parent()[0].offsetLeft;
					to_x -= canvas.offsetLeft;

					// draw the line
					if (! $scope.edgesColors[to][from]) {
						$scope.edgesColors[to][from] = parseInt(Math.random()*colors.length);
					}
					color = colors[$scope.edgesColors[to][from]]
					ctx.fillStyle = color;
					ctx.strokeStyle = color;
					// right arrow will start slightly to the right
					rightArrow = (to_x > from_x);
					xPoint = rightArrow ? ((to_x + from_x)/2 + 3) : ((to_x + from_x)/2 - 3);
					yPoint = rightArrow ? (canvas.height - 2) : (canvas.height - 5);
					r      = rightArrow ? (Math.abs((to_x - from_x)/2) - 3) : (Math.abs((to_x - from_x)/2) + 3);
					ctx.arc(xPoint,yPoint , r, 0, Math.PI, true);
					ctx.stroke();
					// draw the traiangle (arrowhead)
					ctx.beginPath();
					rightArrow ? ctx.moveTo(to_x,canvas.height - 2)     : ctx.moveTo(to_x - 6,canvas.height - 4);
					rightArrow ? ctx.lineTo(to_x + 5,canvas.height - 9) : ctx.lineTo(to_x - 1,canvas.height - 11);
					rightArrow ? ctx.lineTo(to_x - 5,canvas.height - 9) : ctx.lineTo(to_x - 11,canvas.height - 11);
					ctx.fill();
				}
			}
        }
    }

    function parseInputFile(fileText,scope) {
        var allLines = fileText.split("\n");
        scope.nodes = [];
        for (line in allLines) {
            if (allLines[line].trim()) {
                currLine = allLines[line].trim().replace(/\s{2,}/g, ' ').split(" ");
                switch (currLine.shift()) {
                    case "nodes":
                        // define "root" node
                        currLine = ["root"].concat(currLine);
                        // define ids
                        for (i in currLine) {
                            scope.nodes[i] = {text:currLine[i], id:i};
                        }
                        numNodes = scope.nodes.length;
                        // define dimension of edges matrix
                        scope.firstOrderWeights  = new Array(numNodes );
                        scope.secondOrderWeights = new Array(numNodes );
                        for (i=0;i<numNodes ; i++) {
                            scope.firstOrderWeights[i] = new Array(numNodes );
                            scope.secondOrderWeights[i] = new Array(numNodes );
                            for (j=0;j<numNodes  ; j++) {
                                scope.secondOrderWeights[i][j] = new Array(numNodes );
                                for (k=0; k<numNodes ; k++) {
                                    scope.secondOrderWeights[i][j][k] = new Array(numNodes );
                                }
                            }
                        }
                        $scope.allEdges = new Array(numNodes);
						$scope.edgesColors = new Array(numNodes);
						for (var i = 0; i < numNodes; i++) {
							$scope.allEdges[i] = new Array(numNodes)
							$scope.edgesColors[i] = new Array(numNodes);
						}
                        break;
                    case "1stOrder":
                        for (edge in currLine) {
                            edge = currLine[edge].split(",");
                            scope.firstOrderWeights[edge[0]][edge[1]] = edge[2];
                        }
                        break;
                    case "2ndOrder":
                        for (edge in currLine ) {
                            edge = currLine[edge].split(",");
                            scope.secondOrderWeights[edge[0]][edge[1]][edge[2]][edge[3]] = edge[4];
                            scope.secondOrderWeights[edge[2]][edge[3]][edge[0]][edge[1]] = edge[4];
                        }
                        break;
					default:
						window.alert('file parsing error');
						reset();
						return;
                }
            }
        }
    }
	
	$scope.removeEdgesFromInput = function() {
		if ($scope.nodes.length == 0) {
            window.alert("please insert text to randomize on");
            return;
        }
		if ($scope.edgesToRemove == "") {
            window.alert("please insert edges to add");
            return;
        }
		edges = $scope.edgesToRemove.match(/\(\d+,\s*\d+\)/g)
		toList = []
		fromList = []
		for (i in edges) {
			edge = edges[i]
			edge = edge.replace("(","")
			edge = edge.replace(")","")
			edge = edge.replace(", ",",")
			edge = edge.split(",")
			toList = toList.concat(edge[1])
			fromList = fromList.concat(edge[0])
		}
		clearEdges(toList,fromList)
	}
	
	$scope.addEdgesFromInput = function() {
		if ($scope.nodes.length == 0) {
            window.alert("please insert text to randomize on");
            return;
        }
		if ($scope.edgesToAdd == "") {
            window.alert("please insert edges to add");
            return;
        }
		edges = $scope.edgesToAdd.match(/\(\d+,\s*\d+\)/g)
		color = $('input[name="color"]:checked')[0].value
		toList = []
		fromList = []
		for (i in edges) {
			edge = edges[i]
			edge = edge.replace("(","")
			edge = edge.replace(")","")
			edge = edge.replace(", ",",")
			edge = edge.split(",")
			toList = toList.concat(edge[1])
			fromList = fromList.concat(edge[0])
		}
		addEdges(toList,fromList,color)
	}
	
    $scope.generateRandomModel = function() {
        if ($scope.randText == "") {
            window.alert("please insert text to randomize on");
            return;
        }

        nodes = $scope.randText.trim().replace(/\s{2,}/g, ' ').split(" ");

        n = nodes.length + 1;
        out  = "nodes " +  $scope.randText;
        out1 = "1stOrder ";
        for (i = 0 ; i < n ; i++ ) {
            for (j = 0 ; j < n ; j++ ) {
                if (j != i ) {
                    val = Math.random()*3;
                    out1 = out1 + i + "," + j + "," + val + " ";
                }
            }
        }

        out2 = "2ndOrder "
        for (i = 0 ; i < n ; i++ ) {
            for (j = 0 ; j < n ; j++ ) {
                if (j != i ) {
                    for (k = 0 ; k < n ; k++) {
                        for (l = 0 ; l < n ; l++) {
                            if ( ((i != k) || (j != l)) && (l != k) ) {
                                val = Math.random();
                                out2 = out2 + i + "," + j + "," + k + "," + l + "," + val + " ";
                            }
                        }
                    }
                }
            }
        }

        // reset tree vals
        reset();
        parseInputFile(out + "\n" + out1 + "\n" + out2,$scope);
//            $scope.$digest();
    }
	
	// code snip from http://stackoverflow.com/questions/3788125/jquery-querystring
	function querystring(key) {
		var re=new RegExp('(?:\\?|&)'+key+'=(.*?)(?=&|$)','gi');
		var r=[], m;
		while ((m=re.exec(document.location.search)) != null) r.push(m[1]);
		return r;
	}
	
		$(document).keypress(function(event){
		var keycode = (event.keyCode ? event.keyCode : event.which);
		if(keycode == '13'){
			switch (document.activeElement) {
				case $('#randTextBox')[0]:
					$scope.generateRandomModel();
					break;
				case $('#edgesToAddTextBox')[0]:
					$scope.addEdgesFromInput();
					break;
				case $('#edgesToremoveTextBox')[0]:
					$scope.removeEdgesFromInput();
					break;
				default: 
					break;
			}
		}
	});
	
	if (querystring('file') != '') {
		handleChange(querystring('file'));
	}

	
}
