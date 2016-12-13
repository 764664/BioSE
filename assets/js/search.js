import React from 'react';
import ReactDOM from 'react-dom';
import OneItem from './one-item';
import Infinite from 'react-infinite';

class InstantSearch extends React.Component {
    render() {
        if(this.props.terms && this.props.terms.length > 0) {
            return(
                <div className="instant_search">
                    <ul className="list-group">
                        {
                            this.props.terms.map(function(term, index){
                                return(
                                    <li className="list-group-item" key={index} onClick={this.props.click}>{term.name}</li>
                                );
                            }, this)
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

var Filter = React.createClass({
    handleClick: function(index, e){
        console.info(e.target);
        if (e.target.id=="showall") {
            Controller.loadInitialData(undefined, undefined, undefined, "Default");
        }
        else {
            // console.info(e.target.key);
            Controller.loadInitialData(undefined, undefined, undefined, this.props.words[index][0]);
        }
    },
    render: function(){
        return(
            <div>
                <ul>
                    <li onClick={this.handleClick.bind(this, 0)} id="showall">Show All</li>
                    {
                        this.props.words.map(function(word, index){
                            return(
                                <li onClick={this.handleClick.bind(this, index)} key={index}>
                                    {word[0]+" ("+word[1]+")"}
                                </li>
                            )
                        }, this)
                    }
                </ul>
            </div>
        )
    }
});

var OrderBy = React.createClass({
    handleClick: function(e){
        e.preventDefault();
        // console.info(e.target.text);
        Controller.loadInitialData(undefined, 1, e.target.text);
    },
    render: function(){
        return(
            <div className="btn-group navbar-btn" id="order_by">
              <button type="button" className="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                Order By <span className="caret"></span>
              </button>
              <ul className="dropdown-menu">
                <li><a onClick={this.handleClick} href="#">Default</a></li>
                <li role="separator" className="divider"></li>
                <li><a onClick={this.handleClick} href="#">Publication Date(Ascending)</a></li>
                <li><a onClick={this.handleClick} href="#">Publication Date(Descending)</a></li>
              </ul>
            </div>
            )
    }
});

class PaperList extends React.Component {
    render() {
        let papers = this.props.papers;
        if (papers) {
            if (papers.length > 0) {
                return (
                    <div className="paper-list">
                        <ul className="list-group">
                        <Infinite
                            containerHeight={window.innerHeight-110}
                            elementHeight={120}
                            infiniteLoadBeginEdgeOffset={200}
                            useWindowAsScrollContainer={false}
                            onInfiniteLoad={() => {
                                this.props.loadMore();
                            }}
                            // isInfiniteLoading={this.state.isInfiniteLoading}
                        >
                            {
                                papers.map(function (paper, index) {
                                    return (
                                        <OneItem {...this.props} paper={paper} key={index}/>
                                    );
                                }, this)
                            }
                        </Infinite>
                        </ul>
                    </div>
                );
            }
            else {
                return(
                    <p>No result.</p>
                );
            }
        }
        else {
            return null;
        }
    }
}

// class OutPut extends React.Component {
//     render(){
//         return(
//             <div>
//                 <PaperList {...this.props}/>
//                 <Pagination pages={this.props.page_count} current={this.props.current_page} />
//             </div>
//         )
//     }
// }

export default class SearchApp extends React.Component {
    constructor(props) {
        super(props);
        this.state = {text: '', result: '', no_more: false};
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleClick = this.handleClick.bind(this);
        this.onChange = this.onChange.bind(this);
        this.search = this.search.bind(this);
    }

    search() {
        fetch(`/search?keyword=${this.state.text}`)
            .then(response => response.json())
            .then(json => {
                let search_history_id = json.response;
                fetch(`/fetch?search_history_id=${search_history_id}`)
                    .then(response => response.json())
                    .then(json => {
                        this.setState({
                            papers: json.response,
                            search_history_id: search_history_id
                        });
                        $("#loading").modal("hide");
                    })
            })
    }

    loadMore() {
        var length = this.state.papers.length;
        if(length==0) {
            return;
        }
        fetch(`/fetch?search_history_id=${search_history_id}&offset=${length}`)
        .then(response => response.json())
        .then(json => {
            this.setState({papers: this.state.papers.concat(json.response)});
            if(!json.more) {
                this.setState({no_more: true});
            }
        })
    }

    handleSubmit(e) {
        e.preventDefault();
        $("#loading").modal("show");
        this.setState({
            instant_search: null
        });
        location.href=`/#/search/${this.state.text}`;
        this.search();
    }

    handleClick(e) {
        this.setState({
            text: e.target["innerText"],
            instant_search: []
        });
    }

    onChange(e) {
        this.setState({text: e.target.value});
        if(e.target.value.length > 0){
            var xmlhttp = new XMLHttpRequest();
            var url = `/instant?keyword=${e.target.value}`;
            xmlhttp.open("GET", url, true);
            xmlhttp.onload = function() {
                this.setState({instant_search: JSON.parse(xmlhttp.responseText).response});
            }.bind(this);
            xmlhttp.send();
        }
        else {
            this.setState({instant_search: null});
        }
    }

    render() {
        return (
            <div className="container" id="search">
                <div className="row">
                <div className="col-md-12">
                <div className={this.state.papers?'wrapper':'wrapper-init'}>
                <form className="form-inline" id="form_search" onSubmit={this.handleSubmit}>
                    <div className="form-group">
                    <input className="form-control" id="main_search" onChange={this.onChange} value={this.state.text}
                           placeholder="Search" autoComplete="off"/>
                    <InstantSearch terms={this.state.instant_search} click={this.handleClick}/>
                    <button className="btn btn-primary" id="search_button">Search</button>
                    </div>
                </form>

                <PaperList
                    search_app={this}
                    papers={this.state.papers}
                    pages={this.state.page_count}
                    current={this.state.current_page}
                    search_history_id={this.state.search_history_id}
                    loadMore={this.loadMore}
                />
                </div>
                </div>
                </div>
            </div>
        )
    }
}