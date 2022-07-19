'use strict';

exports.handler = (event, context, callback) => {
    console.log(event)    
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    const origin = request.origin;

    //Setup the two different origins
    const originA = "MYBUCKET-1.s3.us-east-1.amazonaws.com";
    const originB = "MYBUCKET-2.s3.us-east-1.amazonaws.com";
    
    origin.authMethod="origin-access-identity";
    origin.region="us_east-1";

    if (Math.random() < 0.5) {
        headers['host'] = [{key: 'host',          value: originA}];
        origin.s3.domainName = originA;
        console.log('Rolled the dice and origin A it is!');
    } else {
        headers['host'] = [{key: 'host',          value: originB}];
        origin.s3.domainName = originB;        
        console.log('Rolled the dice and origin B it is!');
    }

    callback(null, request);
};