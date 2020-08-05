package io.dataline.conduit.server.apis;

import javax.validation.Valid;
import javax.ws.rs.Path;
import java.io.File;
import java.util.List;

import io.dataline.conduit.api.model.ModelApiResponse;
import io.dataline.conduit.api.model.Pet;

@Path("/pet")
public class PetApi implements io.dataline.conduit.api.PetApi {

    @Override
    public Pet addPet(@Valid Pet pet) {
        return null;
    }

    @Override
    public void deletePet(Long petId, String apiKey) {

    }

    @Override
    public List<Pet> findPetsByStatus(String status) {
        return null;
    }

    @Override
    public List<Pet> findPetsByTags(List<String> tags) {
        return null;
    }

    @Override
    public Pet getPetById(Long petId) {
        final Pet pet = new Pet();
        pet.setId(petId);
        return pet;
    }

    @Override
    public Pet updatePet(@Valid Pet pet) {
        return null;
    }

    @Override
    public void updatePetWithForm(Long petId, String name, String status) {

    }

    @Override
    public ModelApiResponse uploadFile(Long petId, String additionalMetadata, @Valid File body) {
        return null;
    }
}
