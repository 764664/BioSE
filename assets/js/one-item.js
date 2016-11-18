import React from 'react';
import ReactDOM from 'react-dom';
import {OverlayTrigger, Popover, Button, Modal} from 'react-bootstrap';

export default class OneItem extends React.Component {
    constructor() {
        super();
        this.popover = this.popover.bind(this);
        this.state = {showModal: false};
    }

    close() {
        this.setState({ showModal: false });
      }

    open() {
        this.setState({ showModal: true });
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
                    <h5>{this.props.paper.title}</h5>
                    <i onClick={this.open.bind(this)} className="material-icons">add</i>
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
                <Modal show={this.state.showModal} onHide={this.close.bind(this)} bsSize="large">
                  <Modal.Header closeButton>
                    <Modal.Title>{this.props.paper.title}</Modal.Title>
                  </Modal.Header>
                  <Modal.Body>
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
                <div className="detail">
                    <a href={"/jump/"}>
                        {this.props.paper.title}
                    </a>
                    <div className="abstract"
                         dangerouslySetInnerHTML={{__html: this.props.paper.abstract.split(this.props.query).join("<span class=\"highlight\">" + this.props.query + "</span>")}}
                    />
                </div>
                </Modal.Body>
                  <Modal.Footer>
                    <Button onClick={this.close.bind(this)}>Close</Button>
                  </Modal.Footer>
                </Modal>
            </li>
        )
    }
}