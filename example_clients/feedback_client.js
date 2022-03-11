var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');

var PROTO_PATH = __dirname + '/../common/feedback.proto';
var packageDefinition = protoLoader.loadSync(PROTO_PATH, { keepCase: true, longs: String, enums: String, defaults: true, oneofs: true });

var feedback_proto = grpc.loadPackageDefinition(packageDefinition).feedback_package;

const SERVER_ADDRESS = 'localhost:50051';

function main() {

    var client = new feedback_proto.FeedbackService(SERVER_ADDRESS, grpc.credentials.createInsecure());

    client.GetMatchingMentor({ menteeUserId: 72 },
        (err, response) => console.log("GetMatchingMentor:", err ? "An error has occurred: " + err : response));
}

main();
