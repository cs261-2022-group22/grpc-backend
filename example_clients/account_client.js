var google_protobuf_timestamp = require('google-protobuf/google/protobuf/timestamp_pb');
var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');

const PROTO_PATH = __dirname + '/../common/account.proto';
const packageDefinition = protoLoader.loadSync(PROTO_PATH, { keepCase: true, longs: String, enums: String, defaults: true, oneofs: true });
const Proto = grpc.loadPackageDefinition(packageDefinition).account_package;
const GRPC_SERVER_ADDRESS = 'localhost:50051';

function main() {

    var client = new Proto.AccountService(GRPC_SERVER_ADDRESS,
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

    client.ListBusinessAreas({},
        (err, resp) => console.log("ListBusinessAreas:", err ? "An error has occurred" : resp))

    client.GetNotifications({ userid: 8, targetProfileType: "MENTOR" },
        (err, response) => console.log("GetNotifications:", err ? "An error has occurred" : response));

    client.RegisterMentee({ userid: 1, desiredSkills: ["Technical", "Management"] },
        (err, response) => console.log("RegisterMentee:", err ? "An error has occurred" : response));

    client.GetMenteesByMentorId({ mentorUserId: 43 },
        (err, response) => console.log("GetMenteesByMentorId:", err ? "An error has occurred" : response));
}

main();
