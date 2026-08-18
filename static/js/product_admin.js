document.addEventListener("DOMContentLoaded", function () {

    const category = document.getElementById("id_category");

    const subcategory = document.getElementById("id_subcategory");

    if (!category || !subcategory) return;

    category.addEventListener("change", function () {

        fetch("/ajax/load-subcategories/?category=" + this.value)

            .then(response => response.json())

            .then(data => {

                subcategory.innerHTML = "";

                data.forEach(function (item) {

                    let option = document.createElement("option");

                    option.value = item.id;

                    option.text = item.name;

                    subcategory.appendChild(option);

                });

            });

    });

});