import React from 'react';
import ReactDOM from 'react-dom';
import {OverlayTrigger, Popover, Button} from 'react-bootstrap';
import Infinite from 'react-infinite';

export default class Subscription extends React.Component {
    constructor(props) {
        super(props);

        this.state = {papers: [], subscriptions: [], no_more: false};
        this.loadData = this.loadData.bind(this);
        this.addSubscription = this.addSubscription.bind(this);
        this.loadSubscription = this.loadSubscription.bind(this);
    }

    addSubscription(keyword) {
        let item = {'keyword': keyword};
        this.setState({subscriptions: this.state.subscriptions.concat([item])});
        var url = `/subscription/add/${keyword}`;
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", url, true);
        xmlhttp.onload = function () {
            if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
            this.loadData();
        }.bind(this);
        xmlhttp.send();
    }

    componentWillMount() {
        this.loadData();
        this.loadSubscription();
    }

    loadData() {
        var url = "/subscription/timeline";
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

    loadMore() {
        var length = this.state.papers.length;
        if(length==0) {
            return;
        }
        var url = `/subscription/timeline?offset=${length}`;
        console.log(`loadMore: ${length}`);
        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("GET", url, true);
        xmlhttp.onload = function () {
            if (xmlhttp.readyState != 4 || xmlhttp.status != 200) return;
            var j = JSON.parse(xmlhttp.responseText);
            // console.info(j);
            this.setState({papers: this.state.papers.concat(j.response)});
            if(!j.more) {
                this.setState({no_more: true});
            }
        }.bind(this);
        xmlhttp.send();
    }

    loadSubscription() {
        let xmlhttp = new XMLHttpRequest();
        const url = "/subscription/index";
        xmlhttp.open("GET", url);
        xmlhttp.onload = () => {
            if (xmlhttp.status >= 200 && xmlhttp.status < 300) {
                console.log(xmlhttp.response);
                this.setState({subscriptions: JSON.parse(xmlhttp.response)});
            }
            else {
                console.log(xmlhttp.statusText);
            }
        }
        xmlhttp.send();
    }

    render() {
        if(this.state.papers) {
            return(
                <div className="container">
                    <div className="row">
                        <div className="col-sm-3">
                            <div className="subscription-management">
                            <SubscriptionManager subscription={this} subscriptions={this.state.subscriptions} />
                            </div>
                        </div>
                        <div className="col-sm-9">
                            <ul className="list-group">
                            <Infinite
                                elementHeight={120}
                                infiniteLoadBeginEdgeOffset={100}
                                useWindowAsScrollContainer={true}
                                onInfiniteLoad={() => {
                                    this.loadMore();
                                }}
                            >
                                {
                                    this.state.papers.map( (paper, index) => {
                                        return(
                                            <OneItem subscription={this} paper={paper} no_more={this.state.no_more} last={index==this.state.papers.length-1}/>
                                        )
                                    })
                                }
                            </Infinite>;
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

class OneItem extends React.Component {
    constructor() {
        super();
        this.popover = this.popover.bind(this);
    }

    handleClickOnAuthor(author) {
        this.props.subscription.addSubscription(author);
    }

    // componentWillMount() {
    //     if(this.props.last && !this.props.no_more) {
    //         this.props.subscription.loadMore();
    //     }
    // }

    popover(author) {
        return(
          <Popover>
            <button type="button" className="btn btn-primary" onClick={() => {this.handleClickOnAuthor(author)}}>Follow</button>
          </Popover>
        );
    }

    render() {
        return(
            <li className="list-group-item one-item">
                <div className="div-title">
                    <h4>{this.props.paper.title}</h4>
                    <a href={this.props.paper.url} className="title" target="_blank"><i className="material-icons">open_in_new</i></a>
                </div>
                <div className="div-authors">
                {
                    this.props.paper.authors.map( (author) => {
                    return(
                        <OverlayTrigger trigger={['focus']} placement="bottom" overlay={this.popover(author)}>
                            <button type="button" className="btn btn-default btn-xs l10">
                              {author}
                            </button>
                        </OverlayTrigger>
                        )
                    })
                }
                </div>
                <div className="meta-info">
                    <div className="meta-info-first">
                    <h6>{this.props.paper.journal}</h6>
                    <h6 className="pub-date">{this.props.paper.date}</h6>
                    </div>
                    <div className="meta-info-second">
                        {
                            this.props.paper.subscriptions.map( (subscription) => {
                                return(
                                    <p className="from-subscription">{subscription}</p>
                                    )
                            })
                        }
                    </div>
                </div>
            </li>
        )
    }
}

class SubscriptionManager extends React.Component {
    render() {
        return(
            <div>
                <AddSubscription {...this.props} subscription_manager={this} />
                <h4>Your subscriptions</h4>
                <div className="subscriptions">
                    {
                        this.props.subscriptions.map( (subscription) => {
                            return(<OneSubscription name={subscription.keyword} />);
                        })
                    }
                </div>
                <h4>Recommended for you</h4>
            </div>
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
        if(this.state.hover) {
            return(
                <div className="subscription">
                    <h6>{this.props.name}</h6>
                    <button type="button" className="btn btn-danger btn-sm btn-follow" onMouseOver={this.mouseOver} onMouseOut={this.mouseOut}>Unfollow</button>
                </div>
            );
        }
        return(
            <div className="subscription">
                <h6>{this.props.name}</h6>
                <button type="button" className="btn btn-primary btn-sm btn-follow" onMouseOver={this.mouseOver} onMouseOut={this.mouseOut}>Following</button>
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
            <div className="subscription-management">
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
            </div>

              </form>
        );
    }
}