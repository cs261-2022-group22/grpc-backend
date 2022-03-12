var grpc = require('@grpc/grpc-js');
var google_protobuf_timestamp = require('google-protobuf/google/protobuf/timestamp_pb');
var protoLoader = require('@grpc/proto-loader');

var PROTO_PATH = __dirname + '/../common/meeting.proto';
var packageDefinition = protoLoader.loadSync(PROTO_PATH, { keepCase: true, longs: String, enums: String, defaults: true, oneofs: true });

var meeting_proto = grpc.loadPackageDefinition(packageDefinition).meeting_package;

const SERVER_ADDRESS = 'localhost:50051';

function main() {

    var client = new meeting_proto.MeetingService(SERVER_ADDRESS, grpc.credentials.createInsecure());

    client.List5AppointmentsByUserID({ userid: 6, profileType: 0 },
        (err, response) => console.log("List5AppointmentsByUserID:", err ? "An error has occurred: " + err : response));

    client.ListPlansOfActions({ userid: 13 },
        (err, response) => console.log("ListPlansOfActions:", err ? "An error has occurred: " + err : response));

    client.TogglePlansOfActionCompletion({ planid: 1 },
        (err, response) => console.log("TogglePlansOfActionCompletion:", err ? "An error has occurred: " + err : response));

    client.CreatePlansOfActions({ menteeUserId: 1, plansOfAction: "Created by JS demo client." },
        (err, response) => console.log("CreatePlansOfActions:", err ? "An error has occurred: " + err : response));

    var exampleStartTime = new google_protobuf_timestamp.Timestamp();
    exampleStartTime.fromDate(new Date());

    client.ScheduleNewMeeting({ menteeUserId: 1, start: exampleStartTime.toObject(), duration: 60, link: "https://meeting.example.com/" },
        (err, response) => console.log("CreatePlansOfActions:", err ? "An error has occurred: " + err : response));
}

main();
