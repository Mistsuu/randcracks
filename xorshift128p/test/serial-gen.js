const gen_serial = () => {
    let serial = ''
    for (let i = 0; i < 32; ++i) {
        if (i == 4 || i == 8 || i == 12 || i == 24)
            serial += '-'
        serial += (Math.random() * 16 | 0).toString(16)
    }
    return serial
}

console.log(gen_serial())  // a61b-454f-7206-41f5127c90bd-b3919692
console.log(gen_serial())  // 1b41-e83d-91c9-e67d26711a35-dc72f582
console.log(gen_serial())  // fe6d-e87e-ef9e-72f0b977fd66-e5433f8f
console.log(gen_serial())  // 9660-7735-5a60-f965eef335b0-170deba4
console.log(gen_serial())  // db90-ff8e-18a7-a94ee6c84e02-5eb905a0
console.log(gen_serial())  // 8b92-196e-de9d-3af97a6cd316-4f74c655