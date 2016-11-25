import React from 'react';
import {OverlayTrigger, Popover, Button, Modal} from 'react-bootstrap';

class TermPopover extends React.Component {
    render() {
        let term = this.props.term;
        return(
            <Popover id="popover-positioned-top" title="Popover top">
                <div>
                    {term.name}
                </div>
                <div>
                    {term.definition}
                </div>
                <div>
                    {term.source}
                </div>
            </Popover>
        )
    }
}

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
            <Popover id="popover-positioned-top" title={<a href={this.renderURL()} target="_blank">{term.name}</a>}>
                <div className="definition">
                    {term.definition}
                </div>
                <div className="source">
                    {term.source}
                </div>
            </Popover>
        );
        return(
            <OverlayTrigger trigger="focus" placement="top" overlay={p}>
               <Button>{term.name}</Button>
            </OverlayTrigger>
        )
    }
}