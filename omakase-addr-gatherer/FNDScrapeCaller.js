// https://stackoverflow.com/questions/62450826/run-python-script-from-node-js-child-process-with-named-arguments

import { spawn } from "child_process"

export function FNDScrape(profileUrl, wallet){
    let scriptOutput = ""
    const child = spawn("python3", [
        // path.join(rootDir, "public", "python", "script.py"),
        "../FNDCongratsBackend/fnd_main.py",
        profileUrl,
        wallet
      ]);
    child.stdout.setEncoding('utf8');
    child.stdout.on('data', function(data) {
        //Here is where the output goes
    
        console.log('stdout: ' + data);
    
        data=data.toString();
        scriptOutput+=data;
    });
    
    child.stderr.setEncoding('utf8');
    child.stderr.on('data', function(data) {
        //Here is where the error output goes
    
        console.log('stderr: ' + data);
    
        data=data.toString();
        scriptOutput+=data;
    });
    
    child.on('close', function(code) {
        //Here you can get the exit code of the script
    
        console.log('closing code: ' + code);
    
        console.log('Full output of script: ',scriptOutput);
    });
}
