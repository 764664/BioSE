import React from 'react';
import ReactDOM from 'react-dom';
import {OverlayTrigger, Popover, Button} from 'react-bootstrap';

export default class OneItem extends React.Component {
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

    renderURL() {
        if (!this.props.display_subscriptions) {
            return(`/jump?search_history_id=${this.props.search_history_id}&paper_id=${this.props.paper.id}`);
        }
        else {
            return(this.props.paper.url);
        }
    }

    renderSubscriptions() {
        if (this.props.display_subscriptions) {
            return(
                <div className="meta-info-second">
                    {
                        this.props.paper.subscriptions.map( (subscription) => {
                            return(
                                <p className="from-subscription">{subscription}</p>
                            )
                        })
                    }
                </div>
            )
        }
        else {
            return null;
        }
    }

    render() {
        return(
            <li className="list-group-item one-item">
                <div className="div-title">
                    <h4>{this.props.paper.title}</h4>
                    <a href={this.renderURL()} className="title" target="_blank"><i className="material-icons">open_in_new</i></a>
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
                        {
                            this.renderSubscriptions()
                        }
                </div>
            </li>
        )
    }
}