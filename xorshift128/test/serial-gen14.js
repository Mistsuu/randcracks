const gen_serial = () => {
    let serial = ''
    for (let i = 0; i < 32; ++i) {
        if (i == 4 || i == 8 || i == 12 || i == 24)
            serial += '-'
        serial += (Math.random() * 14 | 0).toString(16)
    }
    return serial
}

console.log(gen_serial())  // 67a1-1d47-cb35-748ddc6ca763-0cb27a5d
console.log(gen_serial())  // 1b68-2917-0434-c4b7d09dc895-10197c33
console.log(gen_serial())  // 0a74-0653-dd09-dd19541666c1-9ca0bcbc
console.log(gen_serial())  // 5167-a8a6-d975-dab44159d1dc-a14a6d6c
console.log(gen_serial())  // cb49-565d-9a9c-897c171bb8db-8481b44a
console.log(gen_serial())  // 1c5a-9973-8ac5-6967258a57c2-dc8ca105