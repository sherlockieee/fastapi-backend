/*
  Warnings:

  - You are about to drop the column `total_backer` on the `Project` table. All the data in the column will be lost.
  - Added the required column `end_date` to the `Project` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "Project" DROP COLUMN "total_backer",
ADD COLUMN     "end_date" TIMESTAMP(3) NOT NULL,
ADD COLUMN     "total_backers" INTEGER NOT NULL DEFAULT 0;
