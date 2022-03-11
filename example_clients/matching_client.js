var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');

var PROTO_PATH = __dirname + '/../common/matching.proto';
var packageDefinition = protoLoader.loadSync(PROTO_PATH, { keepCase: true, longs: String, enums: String, defaults: true, oneofs: true });

var matching_proto = grpc.loadPackageDefinition(packageDefinition).matching_package;

const SERVER_ADDRESS = 'localhost:50051';

function main() {

    var client = new matching_proto.MatchingService(SERVER_ADDRESS, grpc.credentials.createInsecure());

    client.GetMatchingMentor({ menteeUserId: 72 },
        (err, response) => console.log("GetMatchingMentor:", err ? "An error has occurred: " + err : response));
    
    client.TryMatch({ menteeUserId: 41 }, 
        (err, response) => console.log("TryMatch:", err ? "An error has occurred: " + err : response));
}

main();
