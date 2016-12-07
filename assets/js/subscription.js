import React from 'react';
import ReactDOM from 'react-dom';
import {OverlayTrigger, Popover, Button} from 'react-bootstrap';
import Infinite from 'react-infinite';
import OneItem from './one-item';

export default class Subscription extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            papers: [],
            subscriptions: [],
            no_more: false,
            isInfiniteLoading: false,
            showing: null
        };
        this.loadData = this.loadData.bind(this);
        this.addSubscription = this.addSubscription.bind(this);
        this.removeSubscription = this.removeSubscription.bind(this);
        this.loadSubscription = this.loadSubscription.bind(this);
    }

    addSubscription(keyword, category='keyword') {
        let item = {'keyword': keyword};
        var url = `/subscription/add?keyword=${keyword}`;
        fetch(url, {credentials: 'same-origin'})
        .then(response => response.json())
        .then(json => {
            this.setState({subscriptions: this.state.subscriptions.concat([json.item])});
            this.loadData();
        })
        .catch(error => {
            console.error(error)
        })
    }

    removeSubscription(id) {
        let _index;
        this.state.subscriptions.forEach((value, index) => {
            if(value.id == id) {
                _index = index;
            }
        })
        this.setState({subscriptions: this.state.subscriptions.slice(0, _index).concat(this.state.subscriptions.slice(_index+1))});
        fetch(`/subscription/${id}`, {method: "DELETE", credentials: 'same-origin'})
        .then(response => response.json())
        .catch(error => {
            console.error(error)
        })
    }

    componentWillMount() {
        this.loadData();
        this.loadSubscription();
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevState.showing != this.state.showing) {
            this.loadData();
            this.setState({no_more: false});
        }
    }

    loadData() {
        console.log("loadData");
        if (this.state.showing) {
            var url = `/subscription/${this.state.showing}`;
        }
        else {
            var url = "/subscription/timeline";
        }
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", url, true);
        xmlhttp.onload = function () {
            if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
            var j = JSON.parse(xmlhttp.responseText);
            this.setState({papers: j.response})
        }.bind(this);
        xmlhttp.send();
    }

    loadMore() {
        console.log("preloadMore");
        if(this.state.no_more) {return}
        console.log("loadMore");
        this.setState({isInfiniteLoading: true});
        var length = this.state.papers.length;
        if(length==0) {
            return;
        }
        if (this.state.showing) {
            var url = `/subscription/${this.state.showing}?offset=${length}`;
        }
        else {
            var url = `/subscription/timeline?offset=${length}`;
        }
        console.log(`loadMore: ${length}`);
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", url, true);
        xmlhttp.onload = function () {
            if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
            var j = JSON.parse(xmlhttp.responseText);
            console.info(j.response);
            this.setState({papers: this.state.papers.concat(j.response)});
            if(!j.more) {
                this.setState({no_more: true});
            }
            this.setState({isInfiniteLoading: false});
            console.log("loadMore finish");

        }.bind(this);
        xmlhttp.send();
    }

    loadSubscription() {
        let xmlhttp = new XMLHttpRequest();
        const url = "/subscription/index";
        fetch(url, {credentials: 'same-origin'})
        .then(response => response.json())
        .then(json => {
            this.setState({subscriptions: json.response});
        })
        .catch(error => {console.error(error)});
    }

    render() {
        if(this.state.papers) {
            return(
                <div className="container subscription-container">
                    <div className="row">
                        <div className="col-sm-3">
                            <div className="subscription-management">
                                <SubscriptionManager subscription={this} subscriptions={this.state.subscriptions} />
                            </div>
                        </div>
                        <div className="col-sm-9">
                            <ul className="list-group paper-list">
                            <Infinite
                                containerHeight={window.innerHeight-60}
                                elementHeight={120}
                                infiniteLoadBeginEdgeOffset={200}
                                useWindowAsScrollContainer={false}
                                onInfiniteLoad={() => {

                                    console.log("infi");
                                    this.loadMore();
                                }}
                                // isInfiniteLoading={this.state.isInfiniteLoading}
                            >
                                {
                                    this.state.papers.map( (paper, index) => {
                                        return(
                                            <OneItem
                                                subscription={this}
                                                paper={paper}
                                                no_more={this.state.no_more}
                                                last={index==this.state.papers.length-1}
                                                display_subscriptions={true}
                                            />
                                        )
                                    })
                                }
                            </Infinite>
                            </ul>
                        </div>
                    </div>
                </div>
            )
        }
        else {
            return null;
        }
    }
}

class SubscriptionManager extends React.Component {
    render() {
        return(
            <div className="subscription-manager-outer">
            <div className="subscription-manager-inner">
                <AddSubscription {...this.props} subscription_manager={this} />
                <h4>Your subscriptions</h4>
                <button
                    type="button"
                    className="btn btn-default btn-sm"
                    onClick={() => {this.props.subscription.setState({showing: null})}}
                >Show All</button>
                <div className="subscriptions">
                    {
                        this.props.subscriptions.map( (subscription) => {
                            return(<OneSubscription {...this.props} item={subscription} />);
                        })
                    }
                </div>
                <h4>Recommended for you</h4>
                <RecommendedSubscriptions {...this.props} />
            </div>
            </div>
        )
    }
}

class RecommendedSubscriptions extends React.Component {
    constructor(props) {
      super(props);
      this.state = {recommendations: []};
    }

    componentWillMount() {
        fetch(`/subscription/recommend`, {credentials: 'same-origin'})
        .then(response => response.json())
        .then(json => {
            this.setState({recommendations: json.response.slice(0, 12)});
        })
    }

    render() {
        return(
            <ul className="recommendations">
            {this.state.recommendations.map(item => {
                let keyword = item[0];
                return(
                    <li>
                        <div className="subscription">
                            <h6>{keyword}</h6>
                            <button
                                type="button"
                                className="btn btn-sm btn-follow"
                                onClick={this.props.subscription.addSubscription.bind(this, keyword)}
                            >Follow</button>
                        </div>
                    </li>
                )
            })}
            </ul>
        )
    }
}

class OneSubscription extends React.Component {
    constructor() {
        super();
        this.state = {hover: false};
        this.mouseOver = this.mouseOver.bind(this);
        this.mouseOut = this.mouseOut.bind(this);
    }
    mouseOver() {
        this.setState({hover: true});
    }

    mouseOut() {
        this.setState({hover: false});
    }
    render() {
        return(
            <div className="subscription">
                <button
                    type="button"
                    className="btn btn-default btn-sm"
                    onClick={() => {this.props.subscription.setState({showing: this.props.item.id})}}
                >
                    {this.props.item.keyword}
                </button>
                {this.state.hover?(
                    <button
                        type="button"
                        className="btn btn-danger btn-sm btn-follow"
                        onMouseOver={this.mouseOver}
                        onMouseOut={this.mouseOut}
                        onClick={this.props.subscription.removeSubscription.bind(this, this.props.item.id)}
                    >Unfollow</button>
                ):(
                    <button
                        type="button"
                        className="btn btn-primary btn-sm btn-follow"
                        onMouseOver={this.mouseOver}
                        onMouseOut={this.mouseOut}
                    >Following</button>
                )}
            </div>
        );
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
        this.setState({value: ''});
        this.props.subscription.addSubscription(this.state.value);
    }

    render() {
        return(
            <form className="form-inline">
            <div className="row">
            <div className="col-sm-8">
                <input type="text"
                  placeholder="Subscription"
                  className="form-control"
                  value={this.state.value}
                  onChange={this.handleChange} />
            </div>
            <div className="col-sm-4 follow-button">
                <button onClick={this.handleSubmit} className="btn btn-primary">
                  Follow
                </button>
            </div>
            </div>

              </form>
        );
    }
}

class ShowOneSubscription extends React.Component {
    loadData() {
        var url = `/subscription/${id}`;
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", url, true);
        xmlhttp.onload = function () {
            if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
            var j = JSON.parse(xmlhttp.responseText);
            // console.info(j.response);
            this.setState({papers: j.response})
        }.bind(this);
        xmlhttp.send();
    }

    render() {
        return null;
    }
}