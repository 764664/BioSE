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
                    <ul className="list-group">
                        {
                            this.state.papers.map( (paper) => {
                                return(
                                    <OneItem paper={paper} />
                                )
                            })
                        }
                    </ul>
                </div>
            )
        }
        else {
            return null;
        }
    }
}

class OneItem extends React.Component {
    handleClick(e) {
        console.log("123");
    }

    componentDidMount() {
        $('[data-toggle="popover"]').popover({html:true});
    }

    render() {
        return(
            <li className="list-group-item">
                <div className="div_title"><a href={this.props.paper.url} className="title">{this.props.paper.title}</a></div>
                {this.props.paper.authors.map( (author) => {
                    return(
                        <button type="button" className="btn btn-default l10"
                        data-container="body" data-toggle="popover" data-placement="bottom" data-trigger="focus"
                        data-content="<button class='btn btn-primary'>Follow</button>">
                          {author}
                        </button>
                        )
                })}
                <p>{this.props.paper.date}</p>
            </li>
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
            <form className="form-inline b10">
                <input type="text"
                  placeholder="Subscription"
                  className="form-control"
                  value={this.state.value}
                  onChange={this.handleChange} />
                <button onClick={this.handleSubmit} className="btn btn-primary l10">
                  Follow
                </button>
              </form>
        );
    }
}