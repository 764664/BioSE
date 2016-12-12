import React from 'react';
import {OverlayTrigger, Popover, Button, Modal} from 'react-bootstrap';

export default class Term extends React.Component {
    renderURL() {
        return this.renderURLForTerm(this.props.term.source);
    }
    renderURLForTerm(term) {
        if (term.source == "MeSH") {
            return `https://meshb.nlm.nih.gov/#/record/ui?ui=${term.oid}`;
        }
        else if (term.source == "GO") {
            return `http://amigo.geneontology.org/amigo/term/${term.oid}`;
        }
    }
    render() {
        let term = this.props.term;
        var p =
        (
            <Popover id="popover-positioned-top" className="term-popover" title={
                <div className="term-popover-title">
                    <a href={this.renderURL()} target="_blank"><h5>{term.name}</h5></a>
                    <button type="button" className="btn btn-primary term-popover-follow-btn" onClick={() => {this.props.subscription.addSubscription(term.name)}}>Follow</button>
                </div>
            }>
                {
                    term.definition &&
                    <div className="definition">
                        <h3>Definition</h3>{term.definition}
                    </div>
                }
                {
                    term.ancestors &&
                    <div className="ancestors-div">
                    <h3>Ancestors</h3>
                    <p className="self">{term.name}</p>
                    {
                        term.ancestors.map((ancestor, index) => {
                            return(
                                <div className="ancestors">
                                    {
                                        [...Array(index+1)].map(() => {
                                            return("<");
                                        })
                                    }
                                    <a href={this.renderURLForTerm(ancestor)}>{ancestor.name}</a>
                                </div>
                            )
                        }
                    )}
                    </div>
                }
                {
                    term.source &&
                    <div className="source">
                        <h3>Source</h3>{term.source}
                    </div>
                }
                {
                    term.namespace &&
                    <div>
                        <h3>Namespace</h3>{term.namespace}
                    </div>
                }
                {
                    term.synonyms && term.synonyms.length > 0 &&
                    <div>
                        <h3>Synonyms</h3>{term.synonyms.join(", ")}
                    </div>
                }
            </Popover>
        );
        return(
            <OverlayTrigger trigger="focus" placement="top" overlay={p}>
               <Button>{term.here}</Button>
            </OverlayTrigger>
        )
    }
}