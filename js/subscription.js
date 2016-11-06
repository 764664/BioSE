import React from 'react';
import ReactDOM from 'react-dom';

export default class Subscription extends React.Component {
    constructor(props) {
        super(props);

        this.state = {papers: null};
    }

    componentWillMount() {
        console.log("componentWillMount");
        var url = "/subscription/timeline";
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", url, true);
        xmlhttp.onload = function () {
            if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
            var j = JSON.parse(xmlhttp.responseText);
            console.info(j);
            this.setState({papers: j})
        }.bind(this);
        xmlhttp.send();
    }

    render() {
        if(this.state.papers) {
            return(
                <div>
                <AddSubscription />
                {this.state.papers.map((paper) => {
                    return(
                        <OneItem paper={paper} />
                    );
                })}
                </div>
            )
        }
        else {
            return null;
        }
    }
}

class OneItem extends React.Component {
    render() {
        return(
            <div>
                <h3>{this.props.paper.title}</h3>
                <p>{this.props.paper.authors.join(", ")}</p>
                <p>{this.props.paper.date}</p>
            </div>
        )
    }
}

class AddSubscription extends React.Component {
    constructor(props) {
      super(props);
      this.state = {value: ''};
      this.handleChange = this.handleChange.bind(this);
      this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
      this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        var url = `/subscription/add/${this.state.value}`;
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", url, true);
        xmlhttp.onload = function () {
            if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
            alert(xmlhttp.responseText);
        }.bind(this);
        xmlhttp.send();
    }

    render() {
        return(
            <div>
                <input type="text"
                  placeholder="Subscription"
                  value={this.state.value}
                  onChange={this.handleChange} />
                <button onClick={this.handleSubmit}>
                  Add
                </button>
              </div>
        );
    }
}