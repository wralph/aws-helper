'use strict';

exports.handler = (event, context, callback) => {
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    const origin = request.origin;

    //Setup the two different origins
    const originA = "www.duckduckgo.com";
    const originB = "www.google.com";
    
    if (Math.random() < 0.5) {
        headers['host'] = [{key: 'host',          value: originA}];
        origin.custom.domainName = originA;
        console.log('Rolled the dice and origin A it is!');
    } else {
        headers['host'] = [{key: 'host',          value: originB}];
        origin.custom.domainName = originB;
        console.log('Rolled the dice and origin B it is!');
    }


    callback(null, request);
};