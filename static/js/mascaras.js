// ======================================
// FUNÇÕES GERAIS
// ======================================

function somenteNumeros(valor) {
    return String(valor || "").replace(/\D/g, "");
}


// ======================================
// CPF
// ======================================

function mascaraCPF(valor) {
    valor = somenteNumeros(valor).substring(0, 11);

    valor = valor.replace(
        /^(\d{3})(\d)/,
        "$1.$2"
    );

    valor = valor.replace(
        /^(\d{3})\.(\d{3})(\d)/,
        "$1.$2.$3"
    );

    valor = valor.replace(
        /\.(\d{3})(\d)/,
        ".$1-$2"
    );

    return valor.substring(
        0,
        14
    );
}


// ======================================
// CNPJ
// ======================================

function mascaraCNPJ(valor) {
    valor = somenteNumeros(valor).substring(0, 14);

    valor = valor.replace(
        /^(\d{2})(\d)/,
        "$1.$2"
    );

    valor = valor.replace(
        /^(\d{2})\.(\d{3})(\d)/,
        "$1.$2.$3"
    );

    valor = valor.replace(
        /\.(\d{3})(\d)/,
        ".$1/$2"
    );

    valor = valor.replace(
        /(\d{4})(\d)/,
        "$1-$2"
    );

    return valor.substring(
        0,
        18
    );
}


// ======================================
// CEP
// ======================================

function mascaraCEP(valor) {
    valor = somenteNumeros(valor).substring(0, 8);

    valor = valor.replace(
        /^(\d{5})(\d)/,
        "$1-$2"
    );

    return valor.substring(
        0,
        9
    );
}


// ======================================
// TELEFONE E WHATSAPP
// ======================================

function mascaraTelefone(valor) {
    valor = somenteNumeros(valor).substring(0, 11);

    if (valor.length <= 10) {
        valor = valor.replace(
            /^(\d{2})(\d)/,
            "($1) $2"
        );

        valor = valor.replace(
            /(\d{4})(\d)/,
            "$1-$2"
        );
    } else {
        valor = valor.replace(
            /^(\d{2})(\d)/,
            "($1) $2"
        );

        valor = valor.replace(
            /(\d{5})(\d)/,
            "$1-$2"
        );
    }

    return valor.substring(
        0,
        15
    );
}


// ======================================
// MENSAGEM DO CAMPO CEP
// ======================================

function obterMensagemCEP(campoCEP) {
    let mensagem = campoCEP
        .parentElement
        .querySelector(".mensagem-viacep");

    if (!mensagem) {
        mensagem = document.createElement(
            "div"
        );

        mensagem.className =
            "form-text mensagem-viacep";

        campoCEP.insertAdjacentElement(
            "afterend",
            mensagem
        );
    }

    return mensagem;
}


function exibirMensagemCEP(
    campoCEP,
    texto,
    tipo = "normal"
) {
    const mensagem = obterMensagemCEP(
        campoCEP
    );

    campoCEP.classList.remove(
        "is-valid",
        "is-invalid"
    );

    mensagem.className =
        "form-text mensagem-viacep";

    if (tipo === "sucesso") {
        campoCEP.classList.add(
            "is-valid"
        );

        mensagem.classList.add(
            "text-success"
        );
    } else if (tipo === "erro") {
        campoCEP.classList.add(
            "is-invalid"
        );

        mensagem.classList.add(
            "text-danger"
        );
    } else {
        mensagem.classList.add(
            "text-muted"
        );
    }

    mensagem.textContent = texto;
}


// ======================================
// CAMPOS DO ENDEREÇO
// ======================================

function encontrarCampoNoFormulario(
    formulario,
    nome
) {
    if (!formulario) {
        return null;
    }

    return formulario.querySelector(
        `[name="${nome}"]`
    );
}


function preencherCampo(
    campo,
    valor
) {
    if (!campo) {
        return;
    }

    campo.value = valor || "";

    campo.dispatchEvent(
        new Event(
            "input",
            {
                bubbles: true
            }
        )
    );

    campo.dispatchEvent(
        new Event(
            "change",
            {
                bubbles: true
            }
        )
    );
}


function limparEnderecoViaCEP(
    formulario
) {
    const campos = [
        "rua",
        "bairro",
        "cidade",
        "estado"
    ];

    campos.forEach(function (nome) {
        const campo = encontrarCampoNoFormulario(
            formulario,
            nome
        );

        if (
            campo
            && campo.dataset.preenchidoViacep === "true"
        ) {
            campo.value = "";
            delete campo.dataset.preenchidoViacep;
        }
    });
}


function preencherEnderecoViaCEP(
    formulario,
    dados
) {
    const campos = {
        rua: dados.logradouro,
        bairro: dados.bairro,
        cidade: dados.localidade,
        estado: dados.uf
    };

    Object.entries(
        campos
    ).forEach(function ([nome, valor]) {
        const campo = encontrarCampoNoFormulario(
            formulario,
            nome
        );

        if (!campo) {
            return;
        }

        preencherCampo(
            campo,
            valor
        );

        campo.dataset.preenchidoViacep =
            "true";
    });

    const campoNumero = encontrarCampoNoFormulario(
        formulario,
        "numero"
    );

    if (campoNumero) {
        campoNumero.focus();
    }
}


// ======================================
// CONSULTA VIA CEP
// ======================================

async function consultarViaCEP(
    campoCEP
) {
    const cep = somenteNumeros(
        campoCEP.value
    );

    const formulario = campoCEP.closest(
        "form"
    );

    if (!cep) {
        campoCEP.classList.remove(
            "is-valid",
            "is-invalid"
        );

        return;
    }

    if (cep.length !== 8) {
        exibirMensagemCEP(
            campoCEP,
            "Digite um CEP com 8 números.",
            "erro"
        );

        return;
    }

    campoCEP.disabled = true;

    exibirMensagemCEP(
        campoCEP,
        "Consultando endereço..."
    );

    try {
        const resposta = await fetch(
            `https://viacep.com.br/ws/${cep}/json/`,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

        if (!resposta.ok) {
            throw new Error(
                "Não foi possível consultar o CEP."
            );
        }

        const dados = await resposta.json();

        if (dados.erro) {
            limparEnderecoViaCEP(
                formulario
            );

            exibirMensagemCEP(
                campoCEP,
                "CEP não encontrado.",
                "erro"
            );

            return;
        }

        preencherEnderecoViaCEP(
            formulario,
            dados
        );

        exibirMensagemCEP(
            campoCEP,
            "Endereço encontrado e preenchido.",
            "sucesso"
        );

    } catch (erro) {
        console.error(
            "Erro ao consultar o ViaCEP:",
            erro
        );

        exibirMensagemCEP(
            campoCEP,
            "Não foi possível consultar o CEP. Verifique sua conexão.",
            "erro"
        );

    } finally {
        campoCEP.disabled = false;
    }
}


// ======================================
// APLICAÇÃO DAS MÁSCARAS
// ======================================

function aplicarMascaraCampo(
    campo
) {
    const tipo = campo.dataset.mask;

    switch (tipo) {
        case "cpf":
            campo.value = mascaraCPF(
                campo.value
            );
            break;

        case "cnpj":
            campo.value = mascaraCNPJ(
                campo.value
            );
            break;

        case "cep":
            campo.value = mascaraCEP(
                campo.value
            );
            break;

        case "telefone":
        case "whatsapp":
            campo.value = mascaraTelefone(
                campo.value
            );
            break;
    }
}


// ======================================
// INICIALIZAÇÃO
// ======================================

document.addEventListener(
    "DOMContentLoaded",
    function () {
        const camposComMascara = document.querySelectorAll(
            "[data-mask]"
        );

        camposComMascara.forEach(function (campo) {
            aplicarMascaraCampo(
                campo
            );

            campo.addEventListener(
                "input",
                function () {
                    aplicarMascaraCampo(
                        campo
                    );
                }
            );

            if (campo.dataset.mask === "cep") {
                campo.addEventListener(
                    "blur",
                    function () {
                        consultarViaCEP(
                            campo
                        );
                    }
                );

                campo.addEventListener(
                    "keydown",
                    function (evento) {
                        if (evento.key === "Enter") {
                            evento.preventDefault();

                            consultarViaCEP(
                                campo
                            );
                        }
                    }
                );
            }
        });
    }
);