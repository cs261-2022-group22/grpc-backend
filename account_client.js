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

var PROTO_PATH = __dirname + '/common/account.proto';

var google_protobuf_timestamp = require('google-protobuf/google/protobuf/timestamp_pb');
var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true
    });
var auth_proto = grpc.loadPackageDefinition(packageDefinition).account_package;

function main() {
    var target = 'localhost:50051';

    var client = new auth_proto.AccountService(target,
        grpc.credentials.createInsecure());

    client.TryLogin({ username: 'test@gmail.com', password: 'test' }, function (err, response) {
        if (err) {
            console.log("An error has occurred");
            // console.log(err.message);
            // console.log(err.code);
            //don't log the user in
        }
        else {
            if (response.status === true) { //authenticated so log the user in
                console.log("You are now logged in with id: " + response.id);
            }
            else { //not authenticated
                console.log("Credentials were invalid.")
            }

        }
    });

    const exampleDob = new google_protobuf_timestamp.Timestamp();
    exampleDob.fromDate(new Date());

    client.RegisterUser({
        name: 'Jane Doe',
        password: 'testpassword',
        email: 'janedoe@gmail.com',
        businessAreaId: 1,
        dateOfBirth: exampleDob.toObject()
    }, function (err, response) {
        if (err) {
            console.log("An error has occurred");
            // console.log(err.message);
            // console.log(err.code);
        }
        else {
            if (response.status === true) { //authenticated so log the user in
                console.log("Registration was successful.");
            }
            else { //not authenticated
                console.log("Registration was not successful.")
            }

        }
    });

    client.AccountProfiles({ userid: 1 },
        function (err, response) {
            if (err) {
                console.log("An error has occurred");
            }
            else {
                console.log("isMentor:" + response.isMentor +
                    ";isMentee:" + response.isMentee + ";");
            }
        });

    client.ListBusinessAreas({}, (err, resp) => console.log("ListBusinessAreas:", err ? "An error has occurred" : resp))
}

main();
