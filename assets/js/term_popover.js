import React from 'react';
import {OverlayTrigger, Popover, Button, Modal} from 'react-bootstrap';

export default class Term extends React.Component {
    renderURL() {
        if (this.props.term.source == "MeSH") {
            return `https://meshb.nlm.nih.gov/#/record/ui?ui=${this.props.term.oid}`;
        }
        else if (this.props.term.source == "GO") {
            return `http://amigo.geneontology.org/amigo/term/${this.props.term.oid}`;
        }
    }
    render() {
        let term = this.props.term;
        var p =
        (
            <Popover id="popover-positioned-top" className="term-popover" title={
                <div className="term-popover-title">
                    <a href={this.renderURL()} target="_blank"><h5>{term.name}</h5></a>
                    <button type="button" className="btn btn-primary" onClick={() => {this.props.subscription.addSubscription(term.name)}}>Follow</button>
                </div>
            }>
                {
                    term.definition &&
                    <div className="definition">
                        Definition: {term.definition}
                    </div>
                }
                {
                    term.source &&
                    <div className="source">
                        Source: {term.source}
                    </div>
                }
                {
                    term.namespace &&
                    <div>
                        Namespace: {term.namespace}
                    </div>
                }
                {
                    term.synonyms && term.synonyms.length > 0 &&
                    <div>
                        Synonyms: {term.synonyms.join(", ")}
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