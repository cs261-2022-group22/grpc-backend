/*
 *
 * Copyright 2015 gRPC authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

var PROTO_PATH = __dirname + '/authentication.proto';

var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {keepCase: true,
     longs: String,
     enums: String,
     defaults: true,
     oneofs: true
    });
var auth_proto = grpc.loadPackageDefinition(packageDefinition).authentication;

function main() {
  var target = 'localhost:50051';
  
  var client = new auth_proto.Authenticate(target,
                                       grpc.credentials.createInsecure());
  
  client.TryLogin({username: 'test@gmail.com', password: 'test'}, function(err, response) {
    if (err) {
        console.log("An error has occurred");
        // console.log(err.message);
        // console.log(err.code);
        //don't log the user in
    }
    else {
        if (response.status === "SUCCESS") { //authenticated so log the user in
            console.log("You are now logged in with id: " + response.id);
        }
        else { //not authenticated
            console.log("Credentials were invalid.")
        }
        
    }
  });
}

main();
