import React from 'react';
import ReactDOM from 'react-dom';
import {OverlayTrigger, Popover, Button, Modal} from 'react-bootstrap';
import Term from './term_popover';
const reactStringReplace = require('react-string-replace');

export default class OneItem extends React.Component {
    constructor() {
        super();
        this.popover = this.popover.bind(this);
        this.state = {
            showModal: false,
            abstract: ""
        };
    }

    close() {
        this.setState({ showModal: false });
      }

    open() {
            let abstract = this.props.paper.abstract;
            fetch(`/paper/${this.props.paper.id}`)
            .then(response => response.json())
            .then(json => {
                var terms = json.response;
                terms.forEach(term => {
                    // if(abstract.indexOf(term.name) > -1) {
                    //     abstract = abstract.replace(term.name, `<span class="highlight1 term-${term.id}">${term.name}</span>`)
                    // }

                    // abstract = reactStringReplace(abstract, term.name, (match, i) => (`<span class="highlight1 term-${term.id}">${term.name}</span>`));
                    abstract = reactStringReplace(abstract, term.name, (match, i) => (<Term term={term} />));
                })
                // abstract = abstract.split(this.props.query).join(`<span class="highlight2">${this.props.query}</span>`);
                console.log(abstract);
                this.setState({abstract:abstract});
                console.log("Substituded abstract");
                // let abstract_div = (
                //     <div>
                //         {abstract}
                //     </div>
                // )
                // ReactDOM.render(abstract_div, document.getElementById(`abstract-${this.props.paper.id}`));

            })
            .catch(error => {
                console.log(error);
            })

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
    componentWillMount() {
        this.setState({abstract: this.props.paper.abstract});
    }

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

    renderModal() {
        return(
            <Modal show={this.state.showModal} onHide={this.close.bind(this)} bsSize="large">
              <Modal.Header closeButton>
                <Modal.Title><a href={this.renderURL()}>{this.props.paper.title}</a></Modal.Title>
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
            </div>
            <div className="detail">
                <div className="abstract" id={`abstract-${this.props.paper.id}`}>{this.state.abstract}</div>
            </div>
            </Modal.Body>
              <Modal.Footer>
                <Button onClick={this.close.bind(this)}>Close</Button>
              </Modal.Footer>
            </Modal>
        )
    }

    render() {
        console.log(this.props.paper);
        if(this.props.paper.title && this.props.paper.authors && this.props.paper.authors.length > 0) {
            return(
                <li className="list-group-item one-item" onClick={this.open.bind(this)}>
                    <div className="div-title">
                        <h5>{this.props.paper.title}</h5>
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
                    {this.renderModal()}
                </li>
            )
        }
        else {
            return null;
        }
    }
}