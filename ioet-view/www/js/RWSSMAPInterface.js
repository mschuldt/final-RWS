var NEW_LINE = '<br/>';


function RWSSMAPNode(obj) {
    RWSNode.call(this, 'SMAP', obj);
}
RWSSMAPNode.prototype = new RWSNode();

RWSSMAPNode.prototype.populateInfoPopup = function(container) {
  container.html(dict_to_html(this.infoDict));
}

//NOTE: THIS WON'T Work until we aren't running in the browser because of CORS issues
function RWSSMAPInterface(root_url, available_nodes) {
	var smap = this;
	smap.entries = [];
  this.find_nodes = function() {
    //grab all the nodes
    $.ajax({
       type: 'POST',
       url: root_url,
       data: 'select * where has Metadata/Name;',
       success: function(data) {
          data.forEach(function(datum) {
              smap.add_entry(datum);
          });
       }
       ,
       async:false
    });
  };

  this.add_entry = function(entry) {
        //need to check for duplicates
  	this.entries.push(entry);
  }
    
  this.select_entry = function(entry) {
      var node = new RWSSMAPNode(entry);
      if(entry['Metadata']['Name']) {
        node.name = entry['Metadata']['Name'];
      }
      node.uuid = entry['uuid'];
      if(entry['Actuator'] && entry['Actuator']['Model']) {
        node.add_input(new RWSIOPort(0, node, entry['Actuator']['Model']));
      } else {
        node.add_output();
      }
      //need to check for duplicates
      available_nodes.push(node);
  }

  this.html_for_entry = function(entry) {
  	str = '';
  	if(entry['Actuator'] && entry['Actuator']['Model']) {
  		str += 'Actuator' + NEW_LINE;
      if(entry['Metadata']['Name'])
    		str += 'Name: ' + entry['Metadata']['Name'] + NEW_LINE;
  	} else {
      str += 'Input' + NEW_LINE;
      if(entry['Metadata']['Name'])
    		str += 'Name: ' + entry['Metadata']['Name'] + NEW_LINE;
      if(entry['Metadata']['Sensor'])
        str += 'Sensor: ' + entry['Metadata']['Sensor'] + NEW_LINE;
      if(entry['Properties'] && entry['Properties']['UnitofMeasure'])
        str += 'Units: ' + entry['Properties']['UnitofMeasure'] + NEW_LINE;
  	}
  	return str;
  }
}
